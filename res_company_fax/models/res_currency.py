from odoo import fields, models


class ResCurrency(models.Model):
    _inherit = "res.currency"

    currency_unit_label = fields.Char(translate=True)
    currency_subunit_label = fields.Char(translate=True)
