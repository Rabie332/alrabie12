import calendar
from datetime import date

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HrOvertimeMandate(models.Model):
    _name = "hr.overtime.mandate"
    _inherit = "request"
    _order = "id desc"
    _description = "Overtime mandate"

    amount = fields.Float(string="Amount")
    note = fields.Text(string="Note", readonly=1, states={"draft": [("readonly", 0)]})
    line_ids = fields.One2many(
        "hr.overtime.mandate.line",
        "overtime_mandate_id",
        string="Overtime mandate Lines",
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

    def _sync_employee_details(self):
        for overtime in self:
            super(HrOvertimeMandate, overtime)._sync_employee_details()
            if overtime.employee_id:
                overtime.company_id = overtime.company_id.id

    @api.model
    def create(self, vals):
        """Add sequence."""
        overtime = super(HrOvertimeMandate, self).create(vals)
        if overtime:
            overtime.name = self.env["ir.sequence"].next_by_code(
                "hr.overtime.mandate.seq"
            )
        return overtime

    def action_send(self):
        """Send the request to be approved by the right users."""
        for rec in self:
            if len(rec.line_ids) == 0:
                raise ValidationError(_("Cannot be send because no list."))
            super(HrOvertimeMandate, rec).action_send()

    def action_refuse(self):
        """Check if current record can be cancelled or not."""
        date_today = fields.Date.from_string(fields.Date.today())
        lines = self.line_ids.filtered(lambda l: l.date_from < date_today)
        if lines:
            raise ValidationError(
                _("Cannot be canceled because some missions have started.")
            )
        super(HrOvertimeMandate, self).action_refuse()

    @api.depends("stage_id")
    def _compute_display_button(self):
        for overtime in self:
            super(HrOvertimeMandate, overtime)._compute_display_button()
            users = overtime._get_approvers()
            overtime.display_button_send = False
            overtime.display_button_refuse = False
            overtime.display_button_accept = False
            if overtime.state == "draft" and (
                overtime.env.user.has_group("hr.group_hr_manager")
                or overtime.create_uid.id in users
                or overtime.create_uid.id == overtime.env.user.id
            ):
                overtime.display_button_send = True
            elif overtime.state == "in_progress" and (
                overtime.env.uid in users
                or overtime.env.user.has_group("hr.group_hr_manager")
            ):
                overtime.display_button_accept = True
                overtime.display_button_refuse = True


class HrOvertimeMandateLine(models.Model):
    _name = "hr.overtime.mandate.line"
    _rec_name = "employee_id"
    _order = "id desc"
    _description = "Overtime mandate line"

    # Fields

    overtime_mandate_id = fields.Many2one(
        "hr.overtime.mandate", string="Overtime mandate  ", ondelete="cascade"
    )
    employee_id = fields.Many2one("hr.employee", string=" Employee", required=1)
    type = fields.Selection(
        [
            ("friday_saturday", "Friday and saturday"),
            ("holidays", "Holidays days"),
            ("normal_days", "Normal days"),
        ],
        string="Type",
    )
    hour_number = fields.Integer(string="Hour number")
    date_from = fields.Date(string="Date from", required=1)
    date_to = fields.Date(string="Date to", required=1)
    mission = fields.Text(string="Mission", required=1)
    is_grade = fields.Boolean(string="Is grade", default=False)
    number_direct_overtime = fields.Char(string="Number  ")
    date_direct_overtime = fields.Date(string="Date")
    file_direct_overtime = fields.Binary(
        string="File overtime mandate ", attachment=True
    )
    file_direct_overtime_name = fields.Char(string="File name")
    active = fields.Boolean(default=True)
    employee_ids = fields.Many2many("hr.employee", compute="_compute_employee_ids")

    # ------------------------------------------------------------
    # Compute methods
    # ------------------------------------------------------------
    @api.depends("overtime_mandate_id.employee_id")
    def _compute_employee_ids(self):
        for line in self:
            line.employee_ids = []
            if line.overtime_mandate_id.employee_id:
                employees = (
                    line.env["hr.employee"]
                    .search(
                        [("parent_id", "=", line.overtime_mandate_id.employee_id.id)]
                    )
                    .ids
                )
                line.employee_ids = [(6, 0, employees)]

    # ------------------------------------------------------------
    # Constraints methods
    # ------------------------------------------------------------
    def check_intersection(self):
        overtime_line_id = False
        if isinstance(self.id, int):
            overtime_line_id = self.id
        for rec in self.sudo().search(
            [
                ("id", "!=", overtime_line_id),
                ("employee_id", "=", int(self.employee_id.id)),
                ("overtime_mandate_id.state", "not in", ["refuse", "cancel"]),
            ]
        ):
            if (
                rec.date_from <= self.date_from <= rec.date_to
                or rec.date_from <= self.date_to <= rec.date_to
                or self.date_from <= rec.date_from <= self.date_to
                or self.date_from <= rec.date_to <= self.date_to
            ):
                raise ValidationError(_("Is an overlap in the dates "))

    @api.constrains("date_from", "date_to")
    def _check_dates(self):
        """Check dates."""
        for line in self:
            if line.date_from and line.date_to:
                # Date validation
                if line.date_from > line.date_to:
                    raise ValidationError(
                        _("Start date must be less than the end date.")
                    )
                elif line.date_from.month != line.date_to.month:
                    raise ValidationError(
                        _("Start date and end date must be in the same month.")
                    )
                # Check intersection
                line.check_intersection()

    def overtime_mandate_intersection(self, date_from, date_to, employee_id):
        """Check if employee_id have overtime between date_from, date_to."""
        search_domain = [
            ("employee_id", "=", employee_id),
            ("overtime_mandate_id.state", "not in", ["refuse", "cancel"]),
        ]
        for rec in self.env["hr.overtime.mandate.line"].sudo().search(search_domain):
            if (
                rec.date_from <= date_from <= rec.date_to
                or rec.date_from <= date_to <= rec.date_to
                or date_from <= rec.date_from <= date_to
                or date_from <= rec.date_to <= date_to
            ):
                return True
        return False

    @api.constrains("hour_number")
    def _check_hour_number(self):
        overtime_setting = self.env["hr.overtime.setting"].sudo().search([], limit=1)
        for line in self:
            # check if hour number > 7
            if line.hour_number > overtime_setting.hour_number_mandate:
                raise ValidationError(
                    _("Number of hours must be less than %s hours")
                    % (overtime_setting.hour_number_mandate)
                )
            elif line.hour_number < overtime_setting.min_hour_mandate:
                raise ValidationError(
                    _("Number of hours must be greater than %s hours")
                    % overtime_setting.min_hour_mandate
                )
            # check if hour number <= 0
            elif line.hour_number <= 0:
                raise ValidationError(_("Number of hours must be greater than 0 "))
            token_hours = line.get_token_hours()
            if (
                token_hours
                and token_hours + line.hour_number > overtime_setting.max_hour_month
            ):
                raise ValidationError(
                    _("The number of hours allowed per month has been exceeded")
                )

    def get_token_hours(self):
        """Get token hours in the month."""
        date_from = date(self.date_from.year, self.date_from.month, 1)
        date_to = date(
            self.date_to.year,
            self.date_to.month,
            calendar.monthrange(self.date_to.year, self.date_to.month)[1],
        )
        overtimes = self.search(
            [
                ("employee_id", "=", self.employee_id.id),
                ("overtime_mandate_id.state", "!=", "cancel"),
                ("date_from", ">=", date_from),
                ("date_to", "<=", date_to),
                ("id", "!=", self.id),
            ]
        )
        token_hours = sum(overtimes.mapped("hour_number"))
        return token_hours
