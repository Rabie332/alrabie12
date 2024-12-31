from odoo import fields, models


class HrDepartment(models.Model):
    _inherit = "hr.department"

    name = fields.Char(translate=True)
