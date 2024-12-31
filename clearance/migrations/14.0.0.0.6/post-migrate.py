from odoo.api import Environment


def migrate(cr, version):
    """Update Moves ref."""
    env = Environment(cr, 1, context={})
    moves = (
        env["account.move"]
        .sudo()
        .search([("ref", "=", False), ("clearance_request_id", "!=", False)])
    )
    for move in moves:
        move.ref = move.clearance_request_id.name
        move.invoice_origin = move.clearance_request_id.name
