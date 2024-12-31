from odoo import fields, models


class PosConfig(models.Model):
    _inherit = "pos.config"

    allow_later_payment = fields.Boolean("Later payment")