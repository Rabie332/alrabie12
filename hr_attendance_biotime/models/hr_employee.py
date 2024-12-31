from odoo import fields, models


class HrEmployeeBase(models.AbstractModel):
    _inherit = "hr.employee.base"

    fingerprint_code = fields.Char(string="Fingerprint code", index=1, tracking=True)
