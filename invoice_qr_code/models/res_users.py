from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    code_carrier = fields.Char(string="Code Livreur")
