from odoo.api import Environment


def migrate(cr, version):
    """Remove activities for clearances."""
    env = Environment(cr, 1, context={})
    clearances = (
        env["clearance.request"]
        .sudo()
        .search(
            [("state", "in", ["customs_statement", "transport", "delivery", "close"])]
        )
    )
    activitys = env["mail.activity"].search(
        [
            (
                "activity_type_id",
                "in",
                [
                    env.ref("clearance.mail_translation_officer_approval").id,
                    env.ref("clearance.mail_shipping_agent_responsible_approval").id,
                ],
            ),
            ("res_model", "=", "clearance.request"),
            ("res_id", "in", clearances.ids),
        ]
    )
    activitys.write({"active": False})
