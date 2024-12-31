from odoo.api import Environment


def migrate(cr, version):
    """Update insurance from clearance goods definition."""
    cr.execute("UPDATE clearance_goods_definition SET insurance=temporary_insurance")
    # Drop temporary column
    cr.execute("ALTER TABLE clearance_goods_definition DROP COLUMN temporary_insurance")

    env = Environment(cr, 1, context={})
    clearances = env["clearance.request"].sudo().search([])
    for clearance in clearances:
        invoices = (
            env["clearance.request.invoice"]
            .sudo()
            .search([("clearance_request_id", "=", clearance.id)], order="id asc")
        )
        number = 1
        for invoice in invoices:
            invoice.number = number
            number += 1
