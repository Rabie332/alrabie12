from datetime import datetime

from odoo import _, api, fields, models


class HrDirectAction(models.Model):
    _name = "hr.direct.action"
    _inherit = "request"
    _description = "Direct Action"

    date_direct_action = fields.Date(
        string="Date of commencement",
        required=True,
        readonly=1,
        states={"draft": [("readonly", 0)]},
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
        readonly=1,
        states={"draft": [("readonly", 0)]},
    )
    number = fields.Char(string="Job number", readonly=1)
    refuse_reason = fields.Char(string="Refusal reason")
    employee_id = fields.Many2one(required=1, default=False)
    attachment_ids = fields.Many2many(
        "ir.attachment",
        string="Attachments",
        readonly=1,
        states={"draft": [("readonly", 0)]},
    )

    _sql_constraints = [
        (
            "name_uniq",
            "unique(name)",
            _("The name should be unique!"),
        )
    ]

    @api.depends("stage_id")
    def _compute_display_button(self):
        for rec in self:
            users = rec._get_approvers()
            rec.display_button_refuse = False
            rec.display_button_accept = False
            rec.display_button_send = False
            if rec.state == "draft" and (
                (rec.create_uid and rec.create_uid.id == rec.env.uid)
                or rec.env.user.has_group("hr.group_hr_manager")
            ):
                rec.display_button_send = True
            elif rec.state == "in_progress" and (
                rec.env.uid in users or rec.env.user.has_group("hr.group_hr_manager")
            ):
                rec.display_button_accept = True
                rec.display_button_refuse = True

    def action_accept(self):
        super(HrDirectAction, self).action_accept()
        if self.state == "done":
            self.employee_id.date_direct_action = self.date_direct_action

    def _sync_employee_details(self):
        for request in self:
            super(HrDirectAction, request)._sync_employee_details()
            if request.employee_id:
                request.number = request.employee_id.number

    @api.model
    def create(self, vals):
        """Add sequence."""
        direct_action = super(HrDirectAction, self).create(vals)
        if direct_action:
            for attachment in direct_action.attachment_ids.filtered(
                lambda attachment: not attachment.res_id
            ):
                attachment.res_id = direct_action.id
        direct_action.name = self.env["ir.sequence"].next_by_code(
            "hr.direct.action.seq"
        )
        return direct_action

    def write(self, vals):
        res = super(HrDirectAction, self).write(vals)
        for attachment in self.attachment_ids.filtered(
            lambda attachment: not attachment.res_id
        ):
            attachment.res_id = self.id
        return res

    def _get_day(self, date):
        date = str(date)
        day_name = [
            "الأحد",
            "الإثنين",
            "الثلاثاء",
            "الإربعاء",
            "الخميس",
            "الجمعة",
            "السبت",
        ]
        day_number = datetime.strptime(date, "%Y-%m-%d").strftime("%w")
        day = day_name[int(day_number)]
        return day

    def get_approvals(self, stage_id):
        """Return approver name."""
        for request in self:
            stages = request.sudo().get_approvals_details()
            if stages.get(stage_id, False) and stages[stage_id]["approver"]:
                return stages[stage_id]["approver"].name
            else:
                return ""
