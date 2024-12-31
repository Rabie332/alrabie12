import logging

from odoo.api import Environment

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    env = Environment(cr, 1, context={})
    _logger.info("Start: Change state of expenses")
    for expense_sheet in (
        env["hr.expense.sheet"]
        .sudo()
        .search([("state", "in", ["reviewed", "approve", "approved"])])
    ):
        expense_sheet.state = "submit"
    for expense in (
        env["hr.expense"]
        .sudo()
        .search([("state", "in", ["reviewed", "approve", "approved"])])
    ):
        expense.state = "reported"
    _logger.info("Finish: Change state of expenses")
