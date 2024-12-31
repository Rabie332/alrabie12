from odoo.api import Environment


def migrate(cr, version):
    """Update states room color."""
    env = Environment(cr, 1, context={})
    for room in env["hotel.room"].sudo().search([]):
        room._compute_colors()
