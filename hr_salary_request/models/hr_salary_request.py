from odoo import api, fields, models


class HrSalaryRequest(models.Model):
    _name = "hr.salary.request"
    _inherit = "request"
    _description = "Salary request"

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
        readonly=1,
        states={"draft": [("readonly", 0)]},
    )
    name = fields.Char()
    destined_to = fields.Char(
        string="Destined to",
        required=1,
        readonly=1,
        states={"draft": [("readonly", 0)]},
    )
    number = fields.Char(string="Job number", readonly=1)
    reason = fields.Char(
        string="Reason",
        readonly=1,
        states={"draft": [("readonly", 0)]},
    )
    refuse_reason = fields.Char(string="Refusal reason")
    employee_id = fields.Many2one(string="Employee", required=1)
    type = fields.Selection(
        [
            ("fixing_salary", "Fixing salary"),
            ("definition_of_total", "Definition of total"),
            ("no_salary_definition", "Definition without salary"),
            ("detailed_definition", "Comprehensive detailed definition"),
            ("history_salary_3_months", "Salary of 3 months"),
        ],
        string="Type of request",
        required=1,
        default=False,
        readonly=1,
        states={"draft": [("readonly", 0)]},
    )

    @api.model
    def create(self, values):
        payment = super(HrSalaryRequest, self).create(values)
        payment.name = self.env["ir.sequence"].next_by_code("hr.salary.request.seq")
        return payment

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
        super(HrSalaryRequest, self)._sync_employee_details()
        for request in self:
            if request.employee_id:
                request.number = request.employee_id.number

    def get_approvals(self):
        """Return stage name and approver and his signature."""
        for request in self:
            stages = request.sudo().get_approvals_details()
            approved_stages = []
            for stage in stages:
                approver = stages[stage]["approver"]
                stage_obj = request.env["request.stage"].browse(
                    stages[stage]["stage_id"]
                )

                if stage_obj and stage_obj.appears_in_salary_report:
                    vals = {
                        "stage": stage,
                        "approver_name": approver.name,
                        "signature": False,
                        "sequence": stage_obj.sequence,
                        "date": stages[stage]["date"].strftime("%Y-%m-%d")
                        if stages[stage]["date"]
                        else "",
                    }
                    if approver:
                        vals["signature"] = approver.digital_signature
                    approved_stages.append(vals)
            return sorted(approved_stages, key=lambda i: i["sequence"])

    def print_report(self):
        if self.type == "detailed_definition":
            report_action_name = "hr_salary_request.action_report_detailed_definition"
        elif self.type == "definition_of_total":
            report_action_name = "hr_salary_request.action_report_definition_of_total"
        elif self.type == "fixing_salary":
            report_action_name = "hr_salary_request.action_report_fixing_salary"
        elif self.type == "history_salary_3_months":
            report_action_name = "hr_salary_request.salary_history_xlsx"
        elif self.type == "no_salary_definition":
            report_action_name = "hr_salary_request.action_report_no_salary_definition"
        return self.env.ref(report_action_name).report_action(self.id, config=False)
