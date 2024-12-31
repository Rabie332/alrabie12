from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class HrDeputationExtension(models.Model):
    _name = "hr.deputation.extension"
    _inherit = "request"
    _rec_name = "employee_id"
    _order = "id desc"
    _description = "Deputation Extension"

    deputation_id = fields.Many2one("hr.deputation", string="Deputation", required=1)
    employee_id = fields.Many2one(
        "hr.employee",
        related="deputation_id.employee_id",
        store=True,
        string="Employee",
        readonly=1,
    )
    date_from = fields.Date(string="Date From", required=1, readonly=1)
    duration = fields.Integer(string="Duration", required=1, readonly=1)
    date_to = fields.Date(string="Date To", required=1, readonly=1)
    new_duration = fields.Integer(
        string="Extension Duration",
        required=1,
        readonly=1,
        states={"draft": [("readonly", 0)]},
    )
    reason = fields.Text(
        string="Extension Reason",
        required=1,
        readonly=1,
        states={"draft": [("readonly", 0)]},
    )
    active = fields.Boolean(default=True)
    company_id = fields.Many2one("res.company", string="Company", readonly=1)
    number = fields.Char(string="Job number", readonly=1)
    refuse_reason = fields.Char(string="Refusal reason")

    # ------------------------------------------------------------
    # ORM methods
    # ------------------------------------------------------------
    @api.model
    def create(self, vals):
        """Add sequence."""
        extension = super(HrDeputationExtension, self).create(vals)
        if extension:
            extension.name = self.env["ir.sequence"].next_by_code(
                "hr.deputation.extension.seq"
            )
        return extension

    # ------------------------------------------------------------
    # Constraints methods
    # ------------------------------------------------------------
    @api.constrains("new_duration", "date_from", "date_to")
    def _check_constraints(self):
        """Verify extension time."""
        for rec in self:
            if rec.new_duration <= 0:
                raise UserError(_("Please check the extension time."))
            rec.check_intersection()

    def check_intersection(self):
        """Check intersection with deputation."""
        search_domain = [
            ("employee_id", "=", self.employee_id.id),
            ("state", "=", "done"),
            ("id", "!=", self.deputation_id.id),
        ]
        for rec in self.env["hr.deputation"].search(search_domain):
            if (
                rec.date_from <= self.date_from <= rec.date_to
                or rec.date_from <= self.date_to <= rec.date_to
                or self.date_from <= rec.date_from <= self.date_to
                or self.date_from <= rec.date_to <= self.date_to
            ):
                raise ValidationError(
                    _("There is an overlap of dates with a deputation")
                )

    # ------------------------------------------------------------
    # Onchange methods
    # ------------------------------------------------------------
    @api.onchange("date_from", "date_to", "new_duration")
    def onchange_duration(self):
        """Check constrains and compute date to."""
        self.ensure_one()
        if self.new_duration:
            date_to = str(
                fields.Datetime.from_string(self.date_to)
                + timedelta(days=(self.new_duration - 1))
            )
            # update date_to
            self.date_to = date_to
            self.check_intersection()

    # ------------------------------------------------------------
    # Business methods
    # ------------------------------------------------------------

    def action_accept(self):
        """Accept the request and Send it to be approved by the right users."""
        for rec in self:
            super(HrDeputationExtension, rec).action_accept()
            if rec.state == "done":
                rec.deputation_id.duration += rec.new_duration
                rec.date_to = rec.date_to + timedelta(days=rec.new_duration)
                rec.deputation_id.date_to = rec.date_to
                stock_line = rec.env["hr.employee.deputation.stock"].search(
                    [("employee_id", "=", rec.employee_id.id)], limit=1
                )
                if stock_line:
                    stock_line.token_deputation_sum += rec.new_duration

    # ------------------------------------------------------------
    # Override methods
    # ------------------------------------------------------------

    def _sync_employee_details(self):
        for extension in self:
            super(HrDeputationExtension, extension)._sync_employee_details()
            if extension.employee_id:
                extension.number = extension.employee_id.number
                extension.company_id = extension.company_id.id

    # ------------------------------------------------------------
    # Compute methods
    # ------------------------------------------------------------
    @api.depends("stage_id")
    def _compute_display_button(self):
        for rec in self:
            users = rec._get_approvers()
            rec.display_button_refuse = False
            rec.display_button_accept = False
            rec.display_button_send = False
            if rec.state == "draft" and (
                (rec.create_uid and rec.create_uid.id == rec.env.uid)
                or rec.env.user.has_group("hr_deputation.group_hr_deputation_user")
            ):
                rec.display_button_send = True
            elif rec.state == "in_progress" and (
                rec.env.uid in users
                or rec.env.user.has_group("hr_deputation.group_hr_deputation_user")
            ):
                rec.display_button_accept = True
                rec.display_button_refuse = True
