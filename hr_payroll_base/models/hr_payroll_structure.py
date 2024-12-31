from odoo import fields, models


class HrStructureSalary(models.Model):
    _inherit = "hr.payroll.structure"

    active = fields.Boolean("Active", default=True)
