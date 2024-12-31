from odoo.api import Environment


def migrate(cr, version):
    """Update reward of payments."""
    env = Environment(cr, 1, context={})
    payments = env["account.payment"].sudo().search([("is_reward_drivers", "=", True)])
    for payment in payments:
        for line in payment.shipping_line_ids:
            line.payment_reward_id = payment.id
