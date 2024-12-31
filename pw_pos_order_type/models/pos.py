from odoo import api, fields, models


class PosConfig(models.Model):
    _inherit = "pos.config"

    enable_order_type = fields.Boolean("Enable Order Types")
    order_type_ids = fields.Many2many("pos.order.type", string="order Types")
    default_type_id = fields.Many2one("pos.order.type", string="Default Order Type")


class PosOrder(models.Model):
    _inherit = "pos.order"

    order_type_id = fields.Many2one("pos.order.type", string="Order Type")

    @api.model
    def _order_fields(self, ui_order):
        order_fields = super(PosOrder, self)._order_fields(ui_order)
        if ui_order.get("order_type_id", False):
            order_fields.update({"order_type_id": ui_order["order_type_id"]})
        return order_fields


class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    order_type_id = fields.Many2one(
        "pos.order.type", related="order_id.order_type_id", string="Order Type"
    )
