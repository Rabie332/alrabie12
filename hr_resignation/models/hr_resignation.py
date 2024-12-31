from datetime import datetime

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HrResignation(models.Model):
    _name = "hr.resignation"
    _inherit = ["request"]
    _order = "id desc"
    _description = "Resignation"

    name = fields.Char()
    last_worked_date = fields.Date(
        string="Last worked date",
    )
    resignation_reason = fields.Text(
        string="Resignation reason",
    )

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
    )
    residence_end_date = fields.Date(string="Residence Expiration Date", readonly=1)
    number = fields.Char(string="Job number", readonly=1)
    refuse_reason = fields.Char(string="Refusal reason", readonly=1)
    employee_id = fields.Many2one(readonly=0)
    request_type_id = fields.Many2one(readonly=0)
    is_finished = fields.Boolean("Is Finished")

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

    def _sync_employee_details(self):
        for request in self:
            super(HrResignation, request)._sync_employee_details()
            if request.employee_id:
                request.number = request.employee_id.number
                request.residence_end_date = request.employee_id.residence_end_date

    def action_accept(self):
        for resignation in self:
            super(HrResignation, resignation).action_accept()
            if (
                resignation.stage_id
                and resignation.state == "done"
                and resignation.last_worked_date < fields.Date.today()
            ):
                resignation.employee_id.user_id.active = False
                resignation.employee_id.active = False
                resignation.is_finished = True

    @api.constrains("employee_id")
    def _check_employee_id(self):
        for rec in self:
            if rec.employee_id:
                employee_count = rec.env["hr.resignation"].search_count(
                    [
                        ("employee_id", "=", rec.employee_id.id),
                        ("state", "!=", "cancel"),
                    ]
                )
                if employee_count > 1:
                    raise ValidationError(
                        _("You cannot resign for the same employee more than once.")
                    )

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

    @api.model
    def create(self, vals):
        resignation = super(HrResignation, self).create(vals)
        resignation.name = self.env["ir.sequence"].next_by_code("hr.salary.request.seq")
        # if resgination is created from import
        if resignation.state == "done":
            resignation.stage_id = self.env["request.stage"].search(
                [("res_model", "=", "hr.resignation"), ("state", "=", "done")],
                limit=1,
            )
            if resignation.last_worked_date < fields.Date.today():
                resignation.employee_id.user_id.active = False
                resignation.employee_id.active = False
                resignation.is_finished = True
        return resignation

    @api.model
    def make_employee_archived(self):
        """make in employee and user inactive."""
        for resignation in self.search(
            [
                ("state", "=", "done"),
                ("last_worked_date", "<", fields.Date.today()),
                ("employee_id.active", "=", True),
                ("is_finished", "=", False),
            ]
        ):
            resignation.employee_id.user_id.active = False
            resignation.employee_id.active = False
            resignation.is_finished = True
