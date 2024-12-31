from odoo import api, fields, models


class HrDeputationCancellation(models.Model):
    _name = "hr.deputation.cancellation"
    _inherit = "request"
    _rec_name = "employee_id"
    _order = "id desc"
    _description = "Deputation Cancel"

    deputation_id = fields.Many2one(
        "hr.deputation", string="Deputation", required=1, readonly=1
    )
    employee_id = fields.Many2one(
        "hr.employee",
        related="deputation_id.employee_id",
        store=True,
        string="Employee",
        readonly=1,
    )
    date_from = fields.Date(string="Date From", required=1, readonly=1)
    duration = fields.Integer(string="Duration", required=1, readonly=1)
    date_to = fields.Date(string="Date to", required=1, readonly=1)
    reason = fields.Text(
        string="Cancel Reason", readonly=1, states={"draft": [("readonly", 0)]}
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
        cancellation = super(HrDeputationCancellation, self).create(vals)
        if cancellation:
            cancellation.name = self.env["ir.sequence"].next_by_code(
                "hr.deputation.cancellation.seq"
            )
        return cancellation

    # ------------------------------------------------------------
    # Activity methods
    # ------------------------------------------------------------

    def action_accept(self):
        """Accept the request and Send it to be approved by the right users."""
        for rec in self:
            super(HrDeputationCancellation, rec).action_accept()
            if rec.state == "done":
                stock_line = rec.env["hr.employee.deputation.stock"].search(
                    [("employee_id", "=", rec.employee_id.id)], limit=1
                )
                if stock_line:
                    stock_line.token_deputation_sum -= rec.duration + int(
                        rec.deputation_id.travel_days or 0
                    )
                rec.deputation_id.stage_id = rec.deputation_id._get_next_stage(
                    stage_type="cancel"
                )
                rec.deputation_id._onchange_stage_id()

    # ------------------------------------------------------------
    # Override methods
    # ------------------------------------------------------------
    def _sync_employee_details(self):
        for cancellation in self:
            super(HrDeputationCancellation, cancellation)._sync_employee_details()
            if cancellation.employee_id:
                cancellation.number = cancellation.employee_id.number
                cancellation.company_id = cancellation.company_id.id

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
