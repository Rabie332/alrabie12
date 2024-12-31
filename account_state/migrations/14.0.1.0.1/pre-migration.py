import logging

from odoo.api import Environment

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Update mail_activity_type of mail_activity before data update."""

    env = Environment(cr, 1, context={})
    act_type_data = env["ir.model.data"].search(
        [
            ("module", "=", "account_state"),
            (
                "name",
                "in",
                [
                    "mail_assigned_payment_to_confirm",
                    "mail_assigned_receipt_to_confirm",
                ],
            ),
        ]
    )
    _logger.info(
        "Start: Update mail_activity_type of mail_activity before data update."
    )
    for data in act_type_data:
        data.write({"noupdate": True})
    _logger.info(
        "Finish: Update mail_activity_type of mail_activity before data update."
    )
