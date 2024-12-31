from odoo import fields, models


class HotelFloor(models.Model):

    _inherit = "hotel.floor"

    inspector_id = fields.Many2one("res.users", "Inspector")
