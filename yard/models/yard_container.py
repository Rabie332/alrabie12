from odoo import models, fields, api


class YardContainer(models.Model):
    _name = 'yard.container'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = 'Yard Container'
    _rec_name = "display_name"
    
    name = fields.Char(string='Container Number', required=True)
    zone_id = fields.Many2one('yard.zone', string='Zone')
    is_occupied = fields.Boolean(string="Occupied", compute="_compute_occupancy_status", store=True)
    occupied_by = fields.Many2one('shipping.order.line', string="Occupied By", compute="_compute_occupancy_status", store=True, readonly=True)
    display_name = fields.Char(string='Display Name', compute='_compute_display_name', store=True)
    size = fields.Char(string='Container Size', compute='_compute_container_size', store=True)

    state = fields.Selection(
        [
            ("available", "Available"),
            ("occupied", "Occupied"),
        ],
        default='available',
        string="State",
        tracking=True,
    )

    @api.depends('zone_id', 'state')
    def _compute_occupancy_status(self):
        for record in self:
            occupied_by = self.env['shipping.order.line'].search([
                ('zone_id', '=', record.zone_id.id),
                ('container_id', '=', record.id),
            ], limit=1)
            record.is_occupied = bool(occupied_by)
            record.occupied_by = occupied_by

    @api.depends('name', 'size')
    def _compute_display_name(self):
        for container in self:
            size = container.size or ''
            container.display_name = f"{container.name} ({size}ft)"
    
    @api.depends('zone_id')
    def _compute_container_size(self):
        for container in self:
            if container.zone_id:
                container.size = container.zone_id.zone_type
            else:
                container.size = ''