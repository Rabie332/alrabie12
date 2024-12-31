from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    automatic_employee_number = fields.Boolean(string="Automatic Job number")


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    automatic_employee_number = fields.Boolean(
        string="Automatic Job number",
        related="company_id.automatic_employee_number",
        readonly=False,
    )
