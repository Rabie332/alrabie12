from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    is_payroll_account_batch = fields.Boolean(
        string="Batch Pay Accounting Entry",
        related="company_id.is_payroll_account_batch",
        readonly=False,
    )
