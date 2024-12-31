from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class TruckDriverReservation(models.Model):
    _name = "truck.driver.reservation"
    _description = "Reservations of Trucks and Drivers"
    _rec_name = "vehicle_id"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    vehicle_id = fields.Many2one(
        "fleet.vehicle", string="Reserve Vehicle", tracking=True)
    driver_id = fields.Many2one(
        "res.partner", string="Reserve Driver", tracking=True)
    company_id = fields.Many2one(
        "res.company", string="Company", default=lambda self: self.env.company.id, tracking=True
    )
    is_reserved = fields.Boolean(
        string="Reserved", default=False, tracking=True)

    @api.onchange("vehicle_id")
    def _onchange_vehicle(self):
        if self.vehicle_id and self.vehicle_id.driver_id:
            self.driver_id = self.vehicle_id.driver_id.id

    @api.onchange('is_reserved')
    def _onchange_is_reserved(self):
        if self.is_reserved == True:
            reserved_state = self.env['fleet.vehicle.state'].search(
                [('name', '=', 'Reserved')], limit=1)
            if reserved_state:
                self.vehicle_id.state_id = reserved_state
        else:
            pass


class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'

    def write(self, vals):
        if 'state_id' in vals:
            new_state = self.env['fleet.vehicle.state'].browse(
                vals['state_id'])
            if new_state.name != 'Reserved':
                reservations = self.env['truck.driver.reservation'].search([
                    ('vehicle_id', '=', self.id),
                    ('is_reserved', '=', True)
                ])
                reservations.write({'is_reserved': False})
        return super(FleetVehicle, self).write(vals)


class ShippingOrderLine(models.Model):
    _inherit = "shipping.order.line"

    @api.model
    def create(self, vals):
        # Check if 'vehicle_id' is in the values and if the vehicle is under maintenance
        if 'vehicle_id' in vals:
            # Find the maintenance state
            maintenance_state = self.env['fleet.vehicle.state'].search(
                ['|', ('name', '=', 'تحت الصيانة'), ('name', '=', 'Under maintenance')], limit=1
            )

            # Check if the vehicle is in the maintenance state
            vehicle = self.env['fleet.vehicle'].browse(vals['vehicle_id'])
            if vehicle.state_id == maintenance_state:
                raise ValidationError(
                    _("The vehicle is currently under maintenance and cannot be used for shipping."))

        # Check for driver reservation
        if 'driver_id' in vals:
            # Search for existing reservations
            reservations = self.env['truck.driver.reservation'].search([
                ('vehicle_id', '=', vals['vehicle_id']),
                ('driver_id', '=', vals['driver_id']),
                ('is_reserved', '=', True)
            ])

            if reservations:
                raise ValidationError(
                    _("The driver is already reserved with another vehicle."))

        return super(ShippingOrderLine, self).create(vals)
