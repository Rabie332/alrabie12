from odoo.api import Environment


def migrate(cr, version):
    """Update reward of payments."""
    env = Environment(cr, 1, context={})
    payments = env["account.payment"].sudo().search([("is_reward_drivers", "=", True)])
    for payment in payments:
        payment._compute_residual_reward()
