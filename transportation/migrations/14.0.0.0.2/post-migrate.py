from odoo.api import Environment


def migrate(cr, version):
    """Update payments by shipping order number and request number."""
    env = Environment(cr, 1, context={})
    payments = env["account.payment"].sudo().search([("is_reward_drivers", "=", True)])
    for payment in payments:
        if payment.shipping_order_id:
            payment.shipping_order_number = payment.shipping_order_id.name
        if payment.clearance_request_id:
            payment.request_number = payment.clearance_request_id.name
