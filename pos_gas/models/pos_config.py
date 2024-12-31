from odoo import fields, models


class PosConfig(models.Model):
    _inherit = "pos.config"

    is_gas_station = fields.Boolean("Is Gas Station")
