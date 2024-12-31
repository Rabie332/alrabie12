from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    name = fields.Char(translate=True)
    street = fields.Char(translate=True)
    city = fields.Char(translate=True)
