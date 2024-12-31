from odoo import api, fields, models


class HotelLostFound(models.Model):
    _inherit = "hotel.lost.found"

    partner_room_ids = fields.Many2many("hotel.room", compute="_compute_rooms_partner")

    @api.depends("partner_id")
    def _compute_rooms_partner(self):
        """Get room from partner."""
        for hotel_lost in self:
            domain = []
            if hotel_lost.partner_id:
                domain = [("id", "=", hotel_lost.partner_id.last_room_id.id)]
            hotel_lost.partner_room_ids = (
                hotel_lost.env["hotel.room"].search(domain).ids
            )
