from odoo import _, api, fields, models


class HotelRoom(models.Model):

    _inherit = "hotel.room"
    
    room_branch_id = fields.Many2one(
        "hotel.branch",
        string="Room Branch",
        readonly=True,
        default=lambda self: self.env.user.user_branch_id, 
    )