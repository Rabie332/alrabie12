from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models


class HrDeputationCut(models.Model):
    _name = "hr.deputation.cut"
    _inherit = "request"
    _rec_name = "employee_id"
    _order = "id desc"
    _description = "Deputation Cut"

    deputation_id = fields.Many2one("hr.deputation", string="Deputation", readonly=1)
    employee_id = fields.Many2one(
        "hr.employee",
        related="deputation_id.employee_id",
        store=True,
        string="Employee",
        readonly=1,
    )
    date_from = fields.Date(string="Date From", readonly=1)
    date_to = fields.Date(string="Date to", readonly=1)
    duration = fields.Integer(string="Duration", readonly=1)
    cut_date = fields.Date(
        string="Cut date", readonly=1, states={"draft": [("readonly", 0)]}
    )
    remaining_duration = fields.Integer(
        string="Remaining Duration", compute="_compute_remaining_duration", store=1
    )
    active = fields.Boolean(default=True)

    reason_cut = fields.Text(
        string="Cut Reason", required=1, readonly=1, states={"draft": [("readonly", 0)]}
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        readonly=1,
    )
    number = fields.Char(string="Job number", readonly=1)
    refuse_reason = fields.Char(string="Refusal reason")
    # ------------------------------------------------------------
    # ORM methods
    # ------------------------------------------------------------

    @api.model
    def create(self, vals):
        """Add sequence."""
        vals["name"] = self.env["ir.sequence"].next_by_code("hr.deputation.cut.seq")
        return super(HrDeputationCut, self).create(vals)

    # ------------------------------------------------------------
    # Onchange methods
    # ------------------------------------------------------------
    @api.onchange("deputation_id")
    def _onchange_deputation_id(self):
        """Onchange deputation_id."""
        self.employee_id = self.deputation_id.employee_id
        self.number = self.deputation_id.number
        self.job_id = self.deputation_id.job_id
        self.department_id = self.deputation_id.department_id
        self.company_id = self.deputation_id.company_id
        self.date_from = self.deputation_id.date_from
        self.date_to = self.deputation_id.date_to
        self.duration = self.deputation_id.duration

    @api.onchange("cut_date")
    def _onchange_cut_date(self):
        """Verify.

        i .The date of commencement must be between
        the first day of the assignment and the day before the last of it
        i .The cutoff date must be equal to or greater than today's date
        :return: Dictionary contain a warning key
        """
        if self.cut_date and datetime.today().date() > self.cut_date:
            self.cut_date = False
            warning = {
                "title": _("Warning!"),
                "message": _(
                    "The cutoff date must be equal to or greater than today's date"
                ),
            }
            return {"warning": warning}
        if (
            self.cut_date
            and self.cut_date < self.date_from
            or self.cut_date
            and self.cut_date > self.date_to - relativedelta(days=1)
        ):
            self.cut_date = False
            warning = {
                "title": _("Warning!"),
                "message": _(
                    "The start date must be between the first day "
                    "of the deputation and the day before the last of it"
                ),
            }
            return {"warning": warning}

    # ------------------------------------------------------------
    # Compute methods
    # ------------------------------------------------------------
    @api.depends("cut_date")
    def _compute_remaining_duration(self):
        """Compute remaining duration of the deputation."""
        for rec in self:
            if rec.date_from and rec.date_to and rec.cut_date:
                if rec.date_to >= rec.cut_date >= rec.date_from:
                    rec.remaining_duration = (rec.date_to - rec.cut_date).days + 1

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

    # ------------------------------------------------------------
    # Activity methods
    # ------------------------------------------------------------
    def action_accept(self):
        """Accept the request and Send it to be approved by the right users."""
        for rec in self:
            super(HrDeputationCut, rec).action_accept()
            if rec.state == "done":
                stock_line = rec.env["hr.employee.deputation.stock"].search(
                    [("employee_id", "=", rec.employee_id.id)], limit=1
                )
                if stock_line:
                    stock_line.token_deputation_sum -= rec.remaining_duration
