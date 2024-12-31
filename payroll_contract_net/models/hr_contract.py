from odoo import fields, models


class HrContract(models.Model):
    _inherit = "hr.contract"

    wage_net = fields.Float("Net Wage", digits="Payroll")
