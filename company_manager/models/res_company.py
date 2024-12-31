from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    manager_id = fields.Many2one("res.users", string="Company manager")
