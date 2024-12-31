from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HrAuthorizationWizard(models.TransientModel):
    _name = "hr.authorization.wizard"
    _description = "Hr Authorization Wizard"

    # -----------------------
    # Fields
    # -----------------------

    date_from = fields.Date(string="From Date", required=1)
    date_to = fields.Date(string="To Date", required=1)
    department_id = fields.Many2one("hr.department", string="Department")
    employee_id = fields.Many2one("hr.employee", string="Employee")
    stage_id = fields.Many2one("request.stage", string="Stage")

    # --------------------
    # Constrains Methods
    # --------------------
    @api.constrains("date_from", "date_to")
    def _check_dates(self):
        """Check if date_from less than date_to"""
        for authorization in self:
            if (
                authorization.date_from
                and authorization.date_to
                and authorization.date_from > authorization.date_to
            ):
                raise ValidationError(_("From date must be less than Date to"))

    # --------------------
    # Onchange Methods
    # --------------------
    @api.onchange("department_id")
    def _onchange_department_id(self):
        "Get employees by department"
        employees = {}
        employee_ids = self.env["hr.employee"].search([]).ids
        if self.department_id:
            employee_ids = (
                self.env["hr.employee"]
                .search([("department_id", "=", self.department_id.id)])
                .ids
            )
        employees["domain"] = {"employee_id": [("id", "in", employee_ids)]}
        return employees

    # -------------------
    # Methods
    # -------------------

    def print_report(self):
        """Print Authorization resume report PDF"""
        data = {"ids": [self.id], "form": self.read([])[0]}
        return self.env.ref(
            "hr_authorization.action_report_hr_authorization_resume"
        ).report_action(self, data=data)

    def print_xls_report(self):
        """Print authorization resume report XlSX."""
        data = {"ids": [self.id], "form": self.read([])[0]}
        self.env.ref(
            "hr_authorization.hr_authorization_report_xlsx"
        ).sudo().report_file = _("Hr Authorization Resume Report")
        return self.env.ref(
            "hr_authorization.hr_authorization_report_xlsx"
        ).report_action(self, data=data)
