# See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HotelHousekeepingActivities(models.Model):

    _name = "hotel.housekeeping.activities"
    _description = "Housekeeping Activities"

    housekeeping_id = fields.Many2one("hotel.housekeeping", "Reservation")
    today_date = fields.Date("Today Date")
    activity_id = fields.Many2one("hotel.activity", "Housekeeping Activity")
    housekeeper_id = fields.Many2one("res.users", string="Housekeeper")
    housekeeper_ids = fields.Many2many(
        "res.users", string="Housekeepers", compute="_compute_housekeepers"
    )
    clean_start_time = fields.Datetime("Start Time", required=True)
    clean_end_time = fields.Datetime("End Time", required=True)
    is_dirty = fields.Boolean(
        "Dirty",
        help="Checked if the housekeeping activity" "results as Dirty.",
    )
    is_clean = fields.Boolean(
        "Clean",
        help="Checked if the housekeeping" "activity results as Clean.",
    )
    is_maintenance = fields.Boolean(
        "Maintenance",
        help="Checked if the housekeeping" "activity results as Maintenance.",
    )
    type = fields.Selection(related="housekeeping_id.type", store=1)

    @api.constrains("clean_start_time", "clean_end_time")
    def _check_clean_start_time(self):
        """
        This method is used to validate the clean_start_time and
        clean_end_time.
        ---------------------------------------------------------
        @param self: object pointer
        @return: raise warning depending on the validation
        """
        for activity in self:
            if activity.clean_start_time >= activity.clean_end_time:
                raise ValidationError(_("Start Date Should be less than the End Date!"))

    @api.model
    def default_get(self, fields):
        """
        To get default values for the object.
        @param self: The object pointer.
        @param fields: List of fields for which we want default values
        @return: A dictionary which of fields with values.
        """
        res = super().default_get(fields)
        if self._context.get("room_id", False):
            res.update({"room_id": self._context["room_id"]})
        if self._context.get("today_date", False):
            res.update({"today_date": self._context["today_date"]})
        return res

    @api.depends("type", "housekeeping_id.type")
    def _compute_housekeepers(self):
        """Get housekeepers based on type."""
        for housekeeping in self:
            group = (
                housekeeping.env.ref("hotel_housekeeping.group_maintenance_worker")
                if housekeeping.type == "maintenance"
                else housekeeping.env.ref("hotel_housekeeping.group_clean_worker")
            )
            housekeeping.housekeeper_ids = (
                housekeeping.env["res.users"]
                .search([("groups_id", "in", group.id)])
                .ids
            )

    def write(self, vals):
        """Send activity to housekeeper."""
        housekeeping_activity = super(HotelHousekeepingActivities, self).write(vals)
        if "housekeeper_id" in vals:
            activity = (
                "hotel_housekeeping.mail_assigned_housekeeping_cleanliness_activities"
                if self.housekeeping_id.type == "cleanliness"
                else "hotel_housekeeping.mail_assigned_housekeeping_maintenance_activities"
            )
            self.housekeeping_id.activity_schedule(
                activity,
                user_id=self.housekeeper_id.id,
            )
        return housekeeping_activity

    @api.model
    def create(self, vals):
        """Send activity to housekeeper."""
        housekeeping_activity = super(HotelHousekeepingActivities, self).create(vals)
        activity = (
            "hotel_housekeeping.mail_assigned_housekeeping_cleanliness_activities"
            if housekeeping_activity.housekeeping_id.type == "cleanliness"
            else "hotel_housekeeping.mail_assigned_housekeeping_maintenance_activities"
        )
        housekeeping_activity.housekeeping_id.activity_schedule(
            activity,
            user_id=housekeeping_activity.housekeeper_id.id,
        )
        return housekeeping_activity
