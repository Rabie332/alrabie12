from odoo.api import Environment


def migrate(cr, version):
    """Update Partner of shipping order ."""
    env = Environment(cr, 1, context={})
    for order in env["shipping.order"].search(
        [("clearance_request_id", "!=", False), ("partner_id", "=", False)]
    ):
        order.partner_id = (
            order.clearance_request_id.partner_id.id
            if order.clearance_request_id.partner_id
            else False
        )
