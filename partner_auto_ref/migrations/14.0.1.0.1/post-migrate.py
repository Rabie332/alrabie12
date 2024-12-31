from odoo.api import Environment


def migrate(cr, version):
    """Generate partner_sequence."""
    env = Environment(cr, 1, context={})
    partners = env["res.partner"].search([("company_id", "!=", False)])
    for partner in partners:
        partner._onchange_company()
