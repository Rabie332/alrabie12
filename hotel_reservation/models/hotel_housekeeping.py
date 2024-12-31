from odoo import api, fields, models


class HotelHousekeeping(models.Model):

    _inherit = "hotel.housekeeping"

    reservation_id = fields.Many2one("hotel.reservation", "Reservation", readonly=True)

    def _create_quick_reservation(self, housekeeping):
        """Create quick reservation when housekeeping maintenance created."""
        if housekeeping.type == "maintenance":
            if not len(housekeeping.activity_line_ids):
                check_in = housekeeping.inspect_date_time
                check_out = housekeeping.inspect_date_time
            else:
                check_in = min(
                    housekeeping.activity_line_ids.mapped("clean_start_time")
                )
                check_out = max(housekeeping.activity_line_ids.mapped("clean_end_time"))
            val = {
                "housekeeping_id": housekeeping.id,
                "room_id": housekeeping.room_id.id,
                "check_in": check_in,
                "check_out": check_out,
                "under_maintenance": True,
            }
            housekeeping.env["quick.room.reservation"].create(val)

    @api.model
    def create(self, vals):
        housekeeping = super(HotelHousekeeping, self).create(vals)
        if housekeeping.type == "maintenance":
            housekeeping._create_quick_reservation(housekeeping)
        return housekeeping


class HotelHousekeepingActivities(models.Model):

    _inherit = "hotel.housekeeping.activities"

    def update_quick_reservation(self, housekeeping_activity):
        """Update quick reservation when activities of housekeeping maintenance is changed."""
        if housekeeping_activity.type == "maintenance":
            quick_reservation = self.env["quick.room.reservation"].search(
                [("housekeeping_id", "=", housekeeping_activity.housekeeping_id.id)],
                limit=1,
            )
            check_in = min(
                housekeeping_activity.housekeeping_id.activity_line_ids.mapped(
                    "clean_start_time"
                )
            )
            check_out = max(
                housekeeping_activity.housekeeping_id.activity_line_ids.mapped(
                    "clean_end_time"
                )
            )
            quick_reservation.write({"check_in": check_in, "check_out": check_out})

    def write(self, vals):
        """Update quick reservation."""
        housekeeping_activity = super(HotelHousekeepingActivities, self).write(vals)
        self.update_quick_reservation(self)
        return housekeeping_activity

    @api.model
    def create(self, vals):
        """Update quick reservation."""
        housekeeping_activity = super(HotelHousekeepingActivities, self).create(vals)
        housekeeping_activity.update_quick_reservation(housekeeping_activity)
        return housekeeping_activity
