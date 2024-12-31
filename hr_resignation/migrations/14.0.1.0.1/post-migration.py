import logging

from odoo.api import Environment

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    env = Environment(cr, 1, context={})
    _logger.info("Start: Add sequence for resignation by company")
    for company in env["res.company"].sudo().search([]):
        sequence = env["ir.sequence"].search(
            [("company_id", "=", company.id), ("code", "=", "hr.resignation.seq")],
            limit=1,
        )
        for resignation in (
            env["hr.resignation"]
            .sudo()
            .search([("company_id", "=", company.id)], order="create_date")
        ):
            if sequence:
                resignation.name = sequence._next()
    _logger.info("Finish: Generation sequence for resignation")
