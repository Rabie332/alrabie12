from odoo.api import Environment


def migrate(cr, version):
    """Update cash session."""
    env = Environment(cr, 1, context={})
    sessions = env["pos.session"].sudo().search([("cash_real_difference", "<", 0)])
    for session in sessions:
        session.cash_real_difference = (
            session.cash_real_expected - session.cash_register_balance_end_real
        )
