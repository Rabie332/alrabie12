from odoo import api, fields, models

class HotelReservation(models.Model):
    _inherit = "hotel.reservation"
    
    reservation_branch_id = fields.Many2one(
        "hotel.branch",
        string="Reservation Branch",
        compute="_compute_reservation_branch_id",
        store=True,  # Consider if you need to store the computed value
        readonly=True,
    )

    @api.depends('reservation_line.room_id.room_branch_id')
    def _compute_reservation_branch_id(self):
        for record in self:
            # Assuming reservation_line is a one2many or many2many field, and you want to take the branch of the first line's room
            if record.reservation_line and record.reservation_line[0].room_id:
                record.reservation_branch_id = record.reservation_line[0].room_id.room_branch_id
            else:
                record.reservation_branch_id = False
