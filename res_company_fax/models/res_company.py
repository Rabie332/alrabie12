from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    fax = fields.Char(string="Fax")
    street = fields.Char(translate=True)
    city = fields.Char(translate=True)
