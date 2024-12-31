from odoo import api, fields, models


class PosOrder(models.Model):
    _inherit = "pos.order"

    service_id = fields.Many2one("pos.service")

    @api.model
    def _order_fields(self, ui_order):
        res = super(PosOrder, self)._order_fields(ui_order)
        if ui_order.get("service_id"):
            res["service_id"] = ui_order.get("service_id")
        return res

    def write(self, vals):
        res = super(PosOrder, self).write(vals)
        for order in self:
            if vals.get("state") and vals["state"] == "paid":
                if order.service_id:
                    order.service_id.state = "paid"
        return res