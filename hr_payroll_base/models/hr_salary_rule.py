from odoo import fields, models


class HrSalaryRule(models.Model):
    _inherit = "hr.salary.rule"

    need_to_print = fields.Boolean(string="Need to print")
