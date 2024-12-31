from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    is_payroll_account_batch = fields.Boolean(
        string="Batch Pay Accounting Entry",
    )
