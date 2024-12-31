from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
import logging


_logger = logging.getLogger(__name__)
class HousingUnit(models.Model):
    _name = "housing.unit"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Company Building Units"

    name = fields.Char(compute='_compute_name')
    number = fields.Char(
        string='Unit Number', required=True,
        copy=False, default=lambda self: _('New Unit'),
        help=_("Enter unit number.")
    )
    rooms = fields.Integer()
    bathroom = fields.Integer()
    kitchen = fields.Integer()
    hall = fields.Integer()
    floor = fields.Integer()
    state = fields.Selection(
        [
            ('available', 'Available'),
            ('partially_full', 'Partially Full'),
            ('full', 'Full')
        ],
        string='Unit State',
        default='available',
        tracking=True
    )
    type_id = fields.Many2one(
        "housing.unit.type", string="Unit Type", required=True
    )
    building_id = fields.Many2one(
        "housing.building", string="Building", required=True
    )
    color = fields.Integer(default=10)
    elec_account = fields.Char(string="Electric Meter")
    water_account = fields.Char(string="Water Meter")
    tenant_ids = fields.Many2many('hr.employee', string="Tenants")
    max_capacity = fields.Integer(default=1, required=True)
    max_rate = fields.Integer(string='Maximum rate', default=100)
    occupancy = fields.Float(
        string="Occupancy Percentage", compute='_occupancy')

    @api.model
    def create(self, values):
        record = super(HousingUnit, self).create(values)
        state = record.calculate_current_unit_capacity()
        if state != record.state:
            record.with_context(skip_recursion=True).write({'state': state})
        return record

    def write(self, values):
        if not self.env.context.get('skip_recursion', False):
            res = super(HousingUnit, self).write(values)
            state = self.calculate_current_unit_capacity()
            if state != self.state:
                super(HousingUnit, self).write({'state': state})
            return res
        else:
            return super(HousingUnit, self).write(values)

    def calculate_current_unit_capacity(self):
        for record in self:
            _logger.debug(f"Calculating capacity for {record.id}")
            current_tenants = len(record.tenant_ids)
            _logger.debug(f"Current tenants: {current_tenants}, Max capacity: {record.max_capacity}")
            if current_tenants > record.max_capacity:
                _logger.error("Maximum capacity exceeded")
                raise ValidationError(_("You have exceeded the maximum capacity of the unit."))
            elif current_tenants == record.max_capacity:
                return 'full'
            elif 0 < current_tenants < record.max_capacity:
                return 'partially_full'
            else:
                return 'available'


    def _compute_name(self):
        for record in self:
            record.name = "%s - %s %s" % (record.building_id.name, record.type_id.name, record.number)

    @api.constrains('number', 'building_id', 'type_id')
    def check_contract(self):
        for record in self:
            if self.env['housing.unit'].search([
                ('number', '=', record.number),
                ('id', '!=', record.id),
                ('type_id', '=', record.type_id.id),
                ('building_id', '=', record.building_id.id)
            ]):
                raise ValidationError(
                    _("You cannot add the same unit to the same building.")
                )

    @api.depends('tenant_ids', 'max_capacity')
    def _occupancy(self):
        for record in self:
            if record.max_capacity > 0:
                current_tenants = len(record.tenant_ids)
                record.occupancy = 100.0 * current_tenants / record.max_capacity
            else:
                record.occupancy = 0.0  # To handle edge cases where max_capacity might be zero
