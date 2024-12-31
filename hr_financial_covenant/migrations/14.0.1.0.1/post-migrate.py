from odoo.api import Environment


def migrate(cr, version):
    """Update sequence Financial Covenant."""
    env = Environment(cr, 1, context={})
    financial_covenants = env["hr.financial.covenant"].sudo().search([], order="date")
    for financial_covenant in financial_covenants:
        if not financial_covenant.company_id.financial_covenant_sequence_id:
            IrSequence = env["ir.sequence"].sudo()
            val = {
                "name": "Sequence Financial Covenant "
                + financial_covenant.company_id.name,
                "padding": 5,
                "code": "hr.financial.covenant.seq",
            }
            financial_covenant.company_id.sudo().financial_covenant_sequence_id = (
                IrSequence.create(val).id
            )
        financial_covenant.financial_covenant_number = (
            financial_covenant.company_id.financial_covenant_sequence_id.next_by_id()
        )
