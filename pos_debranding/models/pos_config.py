from odoo import fields, models


class PosConfig(models.Model):
    _inherit = "pos.config"

    display_logo = fields.Boolean(string="Change POS logo")
    pos_logo = fields.Binary(string="POS LOGO")
