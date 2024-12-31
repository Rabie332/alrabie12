from odoo.api import Environment


def migrate(cr, version):
    """Update Routes."""
    env = Environment(cr, 1, context={})
    partner_routes = env["res.partner.clearance.route"].sudo().search([])
    for partner_route in partner_routes:
        partner_route.transport_type = partner_route.route_id.transport_type
        partner_route.company_id = (
            partner_route.route_id.company_id.id
            if partner_route.route_id.company_id
            else False
        )
