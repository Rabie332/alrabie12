from odoo import fields, models


class HrDepartment(models.Model):
    _inherit = 'hr.department'

    department_cost = fields.Float('Department Cost', tracking=True)
    




