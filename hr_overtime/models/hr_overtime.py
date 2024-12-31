import calendar
from datetime import date

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HrOvertime(models.Model):
    _name = "hr.overtime"
    _inherit = "request"
    _description = "Overtimes"

    line_ids = fields.One2many(
        "hr.overtime.line",
        "overtime_id",
        string="Extra hours",
        readonly=1,
        states={"draft": [("readonly", 0)]},
    )
    reason = fields.Text(string="Reason")
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company",
        default=lambda self: self.env.user.company_id,
        required=False,
        readonly=1,
        states={"draft": [("readonly", 0)]},
        string="Company",
    )
    display_button_set_to_draft = fields.Boolean(
        "Display set to draft button", compute="_compute_display_button"
    )

    @api.model
    def create(self, vals):
        """Add sequence."""
        overtime = super(HrOvertime, self).create(vals)
        if overtime:
            overtime.name = self.env["ir.sequence"].next_by_code("hr.overtime.seq")
        return overtime

    @api.depends("stage_id")
    def _compute_display_button(self):
        for overtime in self:
            overtime.display_button_set_to_draft = False
            super(HrOvertime, overtime)._compute_display_button()
            users = overtime._get_approvers()
            if overtime.state == "done" and overtime.env.user.has_group(
                "hr_overtime.group_hr_overtime_manager"
            ):
                overtime.display_button_previous = True
            if (overtime.env.user.id in users and overtime.state == "in_progress") or (
                overtime.state == "done"
                and overtime.env.user.has_group("hr_overtime.group_hr_overtime_manager")
            ):
                overtime.display_button_set_to_draft = True

    def action_previous_stage(self):
        """Return the request to the previous stage."""
        for overtime in self:
            # Return to the previous stage in state done and progress
            if overtime.stage_id and overtime.state in ["done", "in_progress"]:
                overtime.stage_id = overtime._get_previous_stage()
                overtime._onchange_stage_id()
                overtime.activity_update()

    def set_to_draft(self):
        """Set to draft."""
        for overtime in self:
            overtime.stage_id = overtime._get_next_stage(stage_type="default")
            overtime._onchange_stage_id()
            overtime._make_done_activity()
            overtime.activity_schedule(
                "hr_overtime.mail_hr_overtime_set_to_draft",
                user_id=overtime.create_uid.id,
            )


class HrOvertimeLine(models.Model):
    _name = "hr.overtime.line"
    _inherit = ["mail.thread"]
    _order = "id desc"
    _description = "Overtime Line"

    overtime_id = fields.Many2one("hr.overtime", string="Overtime", ondelete="cascade")
    hour_number = fields.Float(string="Hour number", readonly=1)
    date = fields.Date(string="Date", required=1)
    mission = fields.Text(string="Mission", required=1)
    active = fields.Boolean(default=True)
    type = fields.Selection(
        [
            ("friday_saturday", "Friday and saturday"),
            ("holidays", "Holidays days"),
            ("normal_days", "Normal days"),
        ],
        string="Type",
        required=1,
    )
    hour_from = fields.Float(string="Hour From")
    hour_to = fields.Float(string="Hour To")

    @api.onchange("date", "hour_from", "hour_to")
    def _onchange_date(self):
        """Change date."""
        if self.date:
            if fields.Date.from_string(self.date).weekday() in [4, 5]:
                self.type = "friday_saturday"
            else:
                self.type = "normal_days"
            if self.hour_from and self.hour_to:
                self.hour_number = self.hour_to - self.hour_from
            public_holiday_obj = self.env["hr.public.holiday"]
            for public_holiday in public_holiday_obj.search([("state", "=", "done")]):
                if (
                    public_holiday.date_from <= self.date <= public_holiday.date_to
                    or public_holiday.date_from <= self.date <= public_holiday.date_to
                    or self.date <= public_holiday.date_from <= self.date
                    or self.date <= public_holiday.date_to <= self.date
                ):
                    self.type = "holidays"

    def check_overtime_intersection(self):
        """Check Intersection with overtime dates."""
        overtime_line_id = False
        if isinstance(self.id, int):
            overtime_line_id = self.id
        overtime_lines = self.search(
            [
                ("overtime_id.employee_id", "=", self.overtime_id.employee_id.id),
                ("id", "!=", overtime_line_id),
                ("overtime_id.state", "!=", "cancel"),
                ("date", "=", self.date),
            ]
        )
        if len(overtime_lines) > 0:
            raise ValidationError(_("There is an overlap of dates with overtime"))

    @api.constrains("date")
    def _check_date(self):
        """Check Intersection of overtime mandate and extra hours dates."""
        # داخل في التواريخ مع ساعات إضافية
        for overtime_line in self:
            if overtime_line.date:
                # check intersection with other overtime lines
                overtime_line.check_overtime_intersection()
                # check intersection with overtime mandate
                overtime_mandate_lines = (
                    overtime_line.env["hr.overtime.mandate.line"]
                    .sudo()
                    .search(
                        [
                            ("overtime_mandate_id.active", "=", True),
                            (
                                "employee_id",
                                "=",
                                overtime_line.overtime_id.employee_id.id,
                            ),
                            ("overtime_mandate_id.state", "=", "done"),
                        ]
                    )
                )
                for line in overtime_mandate_lines:
                    if line.date_from <= overtime_line.date <= line.date_to:
                        raise ValidationError(
                            _("There is an overlap with overtime mandate dates")
                        )

    @api.constrains("hour_from", "hour_to")
    def _check_hour(self):
        for overtime_line in self:
            # check  hour_to > hour_from
            if (
                overtime_line.hour_from
                and overtime_line.hour_to
                and overtime_line.hour_from >= overtime_line.hour_to
            ):
                raise ValidationError(
                    _("The hour from should be smaller than the hour to")
                )
            # check if hour from and hour to after hors working only at normal_days type
            if overtime_line.type == "normal_days":
                overtime_line._check_employee_schedule()
            # check intersection of overtime hours
            overtime_lines = overtime_line.env["hr.overtime.line"].search(
                [
                    ("id", "!=", overtime_line.id),
                    ("date", "=", overtime_line.date),
                    (
                        "overtime_id.employee_id",
                        "=",
                        overtime_line.overtime_id.employee_id.id,
                    ),
                    ("overtime_id.active", "=", True),
                    ("overtime_id.state", "!=", "cancel"),
                ]
            )
            for rec in overtime_lines:
                if (
                    rec.hour_from <= overtime_line.hour_from <= rec.hour_to
                    or rec.hour_from <= overtime_line.hour_to <= rec.hour_to
                    or overtime_line.hour_from <= rec.hour_from <= overtime_line.hour_to
                    or overtime_line.hour_from <= rec.hour_to <= overtime_line.hour_to
                ):
                    raise ValidationError(_("There is an overlap in overtime."))

    @api.constrains("hour_number")
    def _check_hour_number(self):
        overtime_setting = (
            self.env["hr.overtime.setting"]
            .sudo()
            .search([("type", "=", "overtime")], limit=1)
        )
        for line in self:
            token_hours = line.get_token_hours()
            # check if hour number <= 0
            if line.hour_number <= 0:
                raise ValidationError(_("Number of hours must be greater than 0 "))
            # check normal days hours
            if line.type == "normal_days":
                # check if hour number  greater than max Hours Per Day
                if line.hour_number > overtime_setting.max_hour_day:
                    raise ValidationError(
                        _("Number of hours must be equal or less than %s hours")
                        % (overtime_setting.max_hour_day)
                    )
                # check if hour number  less than min Hours Per Day
                elif line.hour_number < overtime_setting.min_hour_day:
                    raise ValidationError(
                        _("Number of hours must be equal or greater than %s hours")
                        % overtime_setting.min_hour_day
                    )
            # check friday saturday days hours
            elif line.type == "friday_saturday":
                # check if hour number  less than Minimum Hours Per weekend
                if line.hour_number < overtime_setting.min_hour_weekend:
                    raise ValidationError(
                        _("Number of hours must be equal or greater than %s hours")
                        % overtime_setting.min_hour_weekend
                    )
                # check if hour number  greater than max Hours Per weekend
                elif line.hour_number > overtime_setting.max_hour_weekend:
                    raise ValidationError(
                        _("Number of hours must be equal or less than %s hours")
                        % overtime_setting.max_hour_weekend
                    )
            # check if total hour number  in the month greatan than Maximum Hours Per Month
            if (
                token_hours
                and token_hours + line.hour_number > overtime_setting.max_hour_month
            ):
                raise ValidationError(
                    _("The number of hours allowed per month has been exceeded")
                )

    def get_token_hours(self):
        """Get token hours in the month."""
        date_from = date(self.date.year, self.date.month, 1)
        date_to = date(
            self.date.year,
            self.date.month,
            calendar.monthrange(self.date.year, self.date.month)[1],
        )
        overtimes = self.search(
            [
                ("overtime_id.employee_id", "=", self.overtime_id.employee_id.id),
                ("overtime_id.state", "!=", "cancel"),
                ("date", ">=", date_from),
                ("date", "<=", date_to),
                ("id", "!=", self.id),
            ]
        )
        token_hours = sum(overtimes.mapped("hour_number"))
        return token_hours

    # ---------------------------
    # Methods
    # --------------------------

    def _check_employee_schedule(self):
        """check if overtime time after standard hours working."""
        for line in self:
            resource_calendar_attendances = self.env[
                "resource.calendar.attendance"
            ].search(
                [
                    (
                        "calendar_id",
                        "=",
                        line.overtime_id.employee_id.resource_calendar_id.id,
                    ),
                    ("dayofweek", "=", str(line.date.weekday())),
                ]
            )
            for calendar_line in resource_calendar_attendances:
                if (
                    calendar_line.hour_from < line.hour_from < calendar_line.hour_to
                    or calendar_line.hour_from < line.hour_to < calendar_line.hour_to
                ):
                    raise ValidationError(
                        _("You can ask overtime only after hours working")
                    )
