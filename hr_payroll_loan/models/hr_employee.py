from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    loan_ids = fields.One2many("hr.loan", "employee_id", string="Loans")
    loan_count = fields.Integer(
        string="Number of loans", compute="_compute_loans_count", tracking=True
    )

    # ------------------------------------------------------------
    # Compute methods
    # ------------------------------------------------------------
    @api.depends("loan_ids")
    def _compute_loans_count(self):
        for employee in self:
            employee.loan_count = len(employee.loan_ids)
