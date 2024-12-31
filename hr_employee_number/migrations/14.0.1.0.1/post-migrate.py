import logging

from odoo.api import Environment

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Add sequences to companies."""
    env = Environment(cr, 1, context={})
    companies = env["res.company"].search([])
    _logger.info("Start: Add sequences to companies")
    for company in companies:
        if not company.sequence_id:
            IrSequence = company.env["ir.sequence"].sudo()
            val = {
                "name": company.name,
                "padding": 5,
                "code": "res.company",
                "company_id": company.id,
            }
            company.sequence_id = IrSequence.create(val).id
    _logger.info("End: Add sequences to companies")
