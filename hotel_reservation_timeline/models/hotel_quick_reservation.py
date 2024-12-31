from odoo import fields, models


class QuickRoomReservation(models.Model):
    _inherit = "quick.room.reservation"

    is_checked_in = fields.Boolean(related="reservation_id.is_checked_in")
    is_checked_out = fields.Boolean(related="reservation_id.is_checked_out")
    reservation_type = fields.Selection(related="reservation_id.reservation_type")
    reservation_state = fields.Selection(related="reservation_id.state")
