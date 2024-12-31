from odoo.api import Environment


def migrate(cr, version):
    """Update routes of payments."""
    env = Environment(cr, 1, context={})
    payments = env["account.payment"].sudo().search([("is_reward_drivers", "=", True)])
    for payment in payments:
        if payment.shipping_order_id and payment.partner_id:
            lines = payment.shipping_order_id.line_ids.filtered(
                lambda line: line.driver_id == payment.partner_id
            )
            payment.route_ids = [(6, 0, lines.mapped("route_id.id"))]
