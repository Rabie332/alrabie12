from odoo.api import Environment


def migrate(cr, version):
    """Remove activities for moves."""
    env = Environment(cr, 1, context={})
    moves = (
        env["account.move"]
        .sudo()
        .search([("state", "in", ["posted", "cancel", "draft"])])
    )
    activitys = env["mail.activity"].search(
        [
            (
                "activity_type_id",
                "in",
                [
                    env.ref("account_state.mail_assigned_entry_to_confirm").id,
                    env.ref("account_state.mail_assigned_invoice_to_confirm").id,
                    env.ref("account_state.mail_assigned_invoice_to_review").id,
                    env.ref("account_state.mail_assigned_move_to_review").id,
                ],
            ),
            ("res_model", "=", "account.move"),
            ("res_id", "in", moves.ids),
        ]
    )
    activitys.write({"active": False})
