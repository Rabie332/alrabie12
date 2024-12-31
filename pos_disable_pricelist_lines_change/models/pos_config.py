from odoo import fields, models


class PosConfig(models.Model):
    _inherit = "pos.config"

    disable_pricelist_lines_change = fields.Boolean(
        default=False,
    )
