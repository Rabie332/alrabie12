from odoo.api import Environment


def migrate(cr, version):
    """Update authorization."""
    env = Environment(cr, 1, context={})
    authorization = env["hr.authorization"].sudo().search([("id", "=", 332)], limit=1)
    if authorization:
        authorization._compute_authorization_stock()
