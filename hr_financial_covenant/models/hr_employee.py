from odoo import api, fields, models


class Employee(models.Model):
    _inherit = "hr.employee"

    financial_covenant_count = fields.Integer(
        compute="_compute_financial_covenant_count", tracking=True
    )
    financial_covenant_ids = fields.One2many(
        "hr.financial.covenant", "employee_id", string="Financial Covenants"
    )

    @api.depends("financial_covenant_count")
    def _compute_financial_covenant_count(self):
        for employee in self:
            employee.financial_covenant_count = len(
                employee.financial_covenant_ids.filtered(
                    lambda financial_covenant: financial_covenant.state == "done"
                )
            )
