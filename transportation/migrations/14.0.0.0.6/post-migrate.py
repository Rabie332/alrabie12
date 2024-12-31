from odoo.api import Environment


def migrate(cr, version):
    """Update number of shipping order line."""
    env = Environment(cr, 1, context={})
    orders = env["shipping.order"].search([])
    for order in orders:
        number = 1
        for line in order.line_ids:
            line.number = number
            number += 1
