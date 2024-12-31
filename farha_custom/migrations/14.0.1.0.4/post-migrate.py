from odoo.api import Environment


def migrate(cr, version):
    """Attach employee to attachment."""
    env = Environment(cr, 1, context={})
    # Update Dammam Invoices
    for move in (
        env["account.move"]
        .sudo()
        .search(
            [
                ("company_id", "=", 1),
                ("name", "!=", False),
            ]
        )
    ):
        name = move.name
        move.name = name.replace("INV", "DMM-INV")
    # Update Jedah Invoices
    for move in (
        env["account.move"]
        .sudo()
        .search(
            [
                ("company_id", "=", 5),
                ("name", "!=", False),
            ]
        )
    ):
        name = move.name
        move.name = name.replace("INV", "JED-INV")
