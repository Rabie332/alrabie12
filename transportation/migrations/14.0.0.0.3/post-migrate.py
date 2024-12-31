from odoo.api import Environment


def migrate(cr, version):
    """Update reward of payments."""
    env = Environment(cr, 1, context={})
    payments = env["account.payment"].sudo().search([("is_reward_drivers", "=", True)])
    for payment in payments:
        if payment.shipping_order_id:
            lines = payment.shipping_order_id.line_ids.filtered(
                lambda line: line.driver_id == payment.partner_id
            )
            payment.shipping_line_ids = [(6, 0, lines.ids)]
        for line in payment.shipping_order_id.line_ids:
            if (
                line.driver_id == payment.partner_id
                and line in payment.shipping_line_ids
            ):
                line.is_paid = True
