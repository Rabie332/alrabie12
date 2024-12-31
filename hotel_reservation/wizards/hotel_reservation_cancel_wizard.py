from odoo import fields, models


class HotelReservationCancelWizard(models.TransientModel):
    _name = "hotel.reservation.cancel.wizard"
    _description = "Hotel Reservation Finish"

    reservation_id = fields.Many2one("hotel.reservation", string="Reservation")
    reason_cancel = fields.Text(string="Cancel Reason")

    def action_cancel(self):
        """Cancel Reservation"""
        self.reservation_id.write(
            {"reason_cancel": self.reason_cancel, "state": "cancel"}
        )
        room_reservation_line = self.env["hotel.room.reservation.line"].search(
            [("reservation_id", "=", self.reservation_id.id)]
        )
        room_reservation_line.write({"state": "unassigned"})
        room_reservation_line.unlink()
        reservation_lines = self.env["hotel.reservation.line"].search(
            [("line_id", "=", self.reservation_id.id)]
        )
        # for reservation_line in reservation_lines:
        reservation_lines.mapped("room_id").write(
            {"isroom": True, "status": "available"}
        )
