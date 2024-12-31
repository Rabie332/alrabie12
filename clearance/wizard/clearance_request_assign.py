from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ClearanceRequestAssign(models.TransientModel):
    _name = "clearance.request.assign"
    _description = "Clearance Request Assign"

    @api.model
    def _get_users_domain(self):
        # Get right users
        users = (
            self.env["res.users"]
            .search(
                [
                    (
                        "groups_id",
                        "in",
                        [
                            self.env.ref(
                                "clearance.group_shipping_agent_responsible"
                            ).id,
                            self.env.ref("clearance.group_customs_responsible").id,
                            self.env.ref(
                                "clearance.group_customs_declaration_responsible"
                            ).id,
                            self.env.ref("clearance.group_translation_officer").id,
                            self.env.ref("clearance.group_data_entry").id,
                            self.env.ref("clearance.group_reception_responsible").id,
                        ],
                    )
                ]
            )
            .ids
        )
        return [("id", "in", users)]

    user_id = fields.Many2one("res.users", "Responsible", domain=_get_users_domain)

    def action_clearance_assign(self):
        """Assign clearances to selected user."""
        if not self.user_id:
            raise ValidationError(_("User must be fill"))
        clearances = self.env["clearance.request"].search(
            [
                ("id", "in", (self.env.context.get("active_ids"))),
                ("state", "in", ["draft", "customs_clearance", "customs_statement"]),
            ]
        )
        clearances.write({"user_id": self.user_id.id})

    def action_clearance_assign_to_me(self):
        """Assign clearances to me."""
        clearances = self.env["clearance.request"].search(
            [
                ("id", "in", (self.env.context.get("active_ids"))),
                ("state", "in", ["draft", "customs_clearance", "customs_statement"]),
            ]
        )
        clearances.write({"user_id": self.env.user.id})
