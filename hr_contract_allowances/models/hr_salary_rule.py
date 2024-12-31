from odoo import fields, models


class HrPayrollStructure(models.Model):
    _inherit = "hr.salary.rule"

    is_specific_allowance = fields.Boolean(
        string="Specific allowance",
        help="You can select this rule and set an amount for it in the contract's allowances",
    )
