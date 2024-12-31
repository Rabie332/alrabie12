from odoo import fields, models


class PosOrderType(models.Model):
    _name = "pos.order.type"
    _description = "Pos Order Type"

    name = fields.Char("Name", required=True)
