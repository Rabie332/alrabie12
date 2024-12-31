from odoo import models, fields

class HrEmployeeCustom(models.Model):
    _inherit = 'res.company'

    active = fields.Boolean(string="Active", default=True)
