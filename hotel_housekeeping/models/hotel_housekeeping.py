# See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HotelHousekeeping(models.Model):

    _name = "hotel.housekeeping"
    _description = "Hotel Housekeeping"
    _rec_name = "room_id"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    current_date = fields.Date(
        "Today's Date",
        index=True,
        readonly=1,
        default=fields.Date.today,
    )
    clean_type = fields.Selection(
        [("daily", "Daily"), ("checkin", "Check-In"), ("checkout", "Check-Out")],
        "Clean Type",
        states={"done": [("readonly", True)]},
    )
    room_id = fields.Many2one(
        "hotel.room",
        "Room No",
        required=True,
        states={"done": [("readonly", True)]},
        index=True,
    )
    activity_line_ids = fields.One2many(
        "hotel.housekeeping.activities",
        "housekeeping_id",
        "Activities ",
        states={"done": [("readonly", True)]},
        help="Detail of housekeeping \
                                        activities",
    )
    inspector_id = fields.Many2one(
        "res.users",
        "Inspector",
        states={"done": [("readonly", True)]},
    )
    inspect_date_time = fields.Datetime(
        "Inspect Date Time",
        required=True,
        states={"done": [("readonly", True)]},
    )
    quality = fields.Selection(
        [
            ("excellent", "Excellent"),
            ("good", "Good"),
            ("average", "Average"),
            ("bad", "Bad"),
            ("ok", "Ok"),
        ],
        "Quality",
        states={"done": [("readonly", True)]},
        help="Inspector inspect the room and mark \
                                as Excellent, Average, Bad, Good or Ok. ",
    )
    state = fields.Selection(
        [
            ("inspect", "Inspect"),
            ("dirty", "Dirty"),
            ("clean", "Clean"),
            ("maintenance", "Under Maintenance"),
            ("done", "Done"),
            ("cancel", "Cancelled"),
        ],
        "State",
        readonly=True,
        default="inspect",
        tracking=1,
    )
    type = fields.Selection(
        [("cleanliness", "Cleanliness"), ("maintenance", "Maintenance")],
        string="Type",
    )
    note = fields.Text(
        string="Notes",
        states={"done": [("readonly", True)]},
    )
    company_id = fields.Many2one(
        "res.company",
        "Hotel",
        readonly=1,
        states={"inspect": [("readonly", False)]},
        default=lambda self: self.env.company,
    )
    maintenance_type_id = fields.Many2one(
        "hotel.maintenance.type",
        string="Maintenance Type",
        states={"done": [("readonly", True)]},
    )

    categ_id = fields.Many2one(
        "hotel.room.type", "Room Type", states={"done": [("readonly", True)]}
    )

    def action_set_to_dirty(self):
        """
        This method is used to change the state
        to dirty of the hotel housekeeping
        ---------------------------------------
        @param self: object pointer
        """
        self.write({"state": "dirty", "quality": False})
        self.activity_line_ids.write({"is_clean": False, "is_dirty": True})
        self.room_id.is_clean = False

    def room_cancel(self):
        """
        This method is used to change the state
        to cancel of the hotel housekeeping
        ---------------------------------------
        @param self: object pointer
        """
        if self.type == "maintenance":
            self.room_id.button_available()
        self.write({"state": "cancel", "quality": False})

    def room_done(self):
        """
        This method is used to change the state
        to done of the hotel housekeeping
        ---------------------------------------
        @param self: object pointer
        """
        if not self.quality:
            raise ValidationError(_("Please update quality of work!"))
        if self.type == "maintenance":
            self.room_id.button_available()
        self.write({"state": "done"})

    def room_inspect(self):
        """
        This method is used to change the state
        to inspect of the hotel housekeeping
        ---------------------------------------
        @param self: object pointer
        """
        self.write({"state": "inspect", "quality": False})

    def room_clean(self):
        """
        This method is used to change the state
        to clean of the hotel housekeeping
        ---------------------------------------
        @param self: object pointer
        """
        self.write({"state": "clean", "quality": False})
        self.activity_line_ids.write({"is_clean": True, "is_dirty": False})
        self.room_id.is_clean = True

    def action_set_maintenance(self):
        """
        This method is used to change the state
        to maintenance of the hotel housekeeping
        ---------------------------------------
        @param self: object pointer
        """
        self.write({"state": "maintenance", "quality": False})
        self.activity_line_ids.write({"is_maintenance": True})
        self.room_id.status = "maintenance"

    @api.onchange("room_id")
    def _onchange_room(self):
        if self.room_id and self.room_id.floor_id:
            self.inspector_id = self.room_id.floor_id.inspector_id.id

    def write(self, vals):
        """Send activity to inspector."""
        housekeeping = super(HotelHousekeeping, self).write(vals)
        if "inspector_id" in vals:
            activity = (
                "hotel_housekeeping.mail_assigned_housekeeping_cleanliness_request"
                if self.type == "cleanliness"
                else "hotel_housekeeping.mail_assigned_housekeeping_maintenance_request"
            )
            self.activity_schedule(
                activity,
                user_id=self.inspector_id.id,
            )
        return housekeeping

    @api.model
    def create(self, vals):
        """Send activity to inspector."""
        housekeeping = super(HotelHousekeeping, self).create(vals)
        activity = (
            "hotel_housekeeping.mail_assigned_housekeeping_cleanliness_request"
            if housekeeping.type == "cleanliness"
            else "hotel_housekeeping.mail_assigned_housekeeping_maintenance_request"
        )
        if housekeeping.inspector_id:
            housekeeping.activity_schedule(
                activity,
                user_id=housekeeping.inspector_id.id,
            )
        return housekeeping
