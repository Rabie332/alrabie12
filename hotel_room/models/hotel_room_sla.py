from datetime import datetime

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class RoomStatusSla(models.Model):
    _name = "room.status.sla"
    _description = "Room Status SLA"

    status = fields.Selection(
        string="Status",
        selection=[("dirty", "Dirty"), ("maintenance", "Maintenance")],
        default="dirty",
        required=1,
    )
    unity_number = fields.Integer(string="Number", required=1)
    unity = fields.Selection(
        [("hour", "Hour"), ("day", "Day"), ("month", "Month")],
        default="hour",
        string="Unity",
        required=1,
    )
    message = fields.Text(string="Message", required=1, translate=1)
    user_ids = fields.Many2many("res.users", string="Users", required=1)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company",
        "Hotel",
        required=True,
        default=lambda self: self.env.company,
    )

    @api.constrains("status")
    def _check_status(self):
        """CHeck Status."""
        for sla in self:
            if sla.search(
                [
                    ("status", "=", sla.status),
                    ("company_id", "=", sla.company_id.id),
                    ("id", "!=", sla.id),
                ]
            ):
                raise ValidationError(
                    _("You can't have the same SLA for the same status %s")
                    % _(
                        dict(
                            sla._fields["status"]._description_selection(
                                self.with_context({"lang": self.env.user.lang}).env
                            )
                        ).get(sla.status)
                    )
                )

    def get_duration_status_room(self, date_from, date_to, unity):
        """Get duration for change rooms"""
        if unity == "day":
            duration = (date_to.date() - date_from.date()).days
        elif unity == "month":
            duration = (date_to.date() - date_from.date()).days / 30
        else:
            duration = (date_to - date_from).total_seconds() / 3600
        return round(duration)

    @api.model
    def cron_room_status_sla(self):
        """Notify users about status SLa"""
        today = datetime.today()
        # send mail if the room is in maintenance and equal
        # or greater then duration in sla setting
        for room in self.env["hotel.room"].search(
            [("status", "=", "maintenance"), ("is_send_mail_maintenance", "=", False)]
        ):
            sla_setting_maintenance = self.search(
                [
                    ("status", "=", "maintenance"),
                    ("company_id", "=", room.company_id.id),
                ],
                limit=1,
            )
            date_tracking_maintenance = (
                self.env["mail.tracking.value"]
                .sudo()
                .search(
                    [
                        ("mail_message_id.model", "=", "hotel.room"),
                        ("mail_message_id.res_id", "=", room.id),
                        ("new_value_char", "in", ["In maintenance", "في الصيانة"]),
                    ],
                    limit=1,
                    order="id desc",
                )
                .mail_message_id.date
            )
            # send mail if the room is dirty and equal or greater then duration in sla setting
            if sla_setting_maintenance.unity_number and date_tracking_maintenance:
                duration = self.get_duration_status_room(
                    date_tracking_maintenance, today, sla_setting_maintenance.unity
                )
                if duration >= sla_setting_maintenance.unity_number:
                    room.message_post(
                        body=sla_setting_maintenance.message,
                        partner_ids=[
                            user.partner_id.id
                            for user in sla_setting_maintenance.user_ids
                        ],
                    )
                    room.is_send_mail_maintenance = True

        for room_dirty in self.env["hotel.room"].search(
            [("is_clean", "=", False), ("is_send_mail_dirty", "=", False)]
        ):
            sla_setting_dirty = self.search(
                [
                    ("status", "=", "dirty"),
                    ("company_id", "=", room_dirty.company_id.id),
                ],
                limit=1,
            )
            date_tracking_dirty = (
                self.env["mail.tracking.value"]
                .sudo()
                .search(
                    [
                        ("mail_message_id.model", "=", "hotel.room"),
                        ("mail_message_id.res_id", "=", room_dirty.id),
                        ("new_value_integer", "=", 0),
                    ],
                    limit=1,
                    order="id desc",
                )
                .mail_message_id.date
            )
            if sla_setting_dirty.unity_number and date_tracking_dirty:
                duration = self.get_duration_status_room(
                    date_tracking_dirty, today, sla_setting_dirty.unity
                )
                if duration >= sla_setting_dirty.unity_number:
                    room_dirty.message_post(
                        body=sla_setting_dirty.message,
                        partner_ids=[
                            user.partner_id.id for user in sla_setting_dirty.user_ids
                        ],
                    )
                    room_dirty.is_send_mail_dirty = True
