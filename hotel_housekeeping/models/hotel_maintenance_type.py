from odoo import fields, models


class HotelMaintenanceType(models.Model):

    _name = "hotel.maintenance.type"
    _description = "Maintenance Types"

    name = fields.Char(string="Name", translate=1, required=1)
    active = fields.Boolean(string="Active", default=True)
