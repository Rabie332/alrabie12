from odoo import fields, models


class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    shipping_orders_number = fields.Integer(
        string="Shipping orders number", compute="_compute_shipping_orders"
    )

    # ------------------------------------------------------
    # Business Methods
    # ------------------------------------------------------

    def shipping_orders_action(self):
        """Get reward for drivers."""
        action = self.env.ref("transportation.shipping_order_action").sudo().read()[0]
        action["domain"] = [("line_ids.vehicle_id", "=", self.id)]
        action["context"] = {
            "no_create_edit": True,
        }
        return action

    # ------------------------------------------------------------
    # Compute methods
    # ------------------------------------------------------------

    def _compute_shipping_orders(self):
        """Calculate payments drivers."""
        for request in self:
            request.shipping_orders_number = request.env["shipping.order"].search_count(
                [("line_ids.vehicle_id", "=", self.id)]
            )
