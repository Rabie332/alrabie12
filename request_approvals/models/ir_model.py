from odoo import fields, models


class IrModel(models.Model):
    _inherit = "ir.model"

    can_approve = fields.Boolean("Can Approve")
    image_128 = fields.Image("Logo", max_width=128, max_height=128)
