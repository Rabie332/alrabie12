import logging

from odoo.api import Environment

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    env = Environment(cr, 1, context={})
    _logger.info("Start: Add sequence for deputation by company")
    for company in env["res.company"].sudo().search([]):
        sequence = env["ir.sequence"].search(
            [("company_id", "=", company.id), ("code", "=", "hr.deputation.seq")]
        )
        for deputation in (
            env["hr.deputation"]
            .sudo()
            .search([("company_id", "=", company.id)], order="create_date")
        ):
            deputation.name = sequence._next()
    _logger.info("Finish: Generation sequence for deputations")
