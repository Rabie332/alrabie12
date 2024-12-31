from odoo import fields, models


class PosConfig(models.Model):
    _inherit = "pos.config"

    extra_products = fields.Boolean(string="Extra products", default=True)
