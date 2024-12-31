from odoo import _, api, models


class ResUsers(models.Model):
    _inherit = "res.users"

    # ------------------------------------------------------------
    # Business methods
    # ------------------------------------------------------------
    @api.model
    def get_approval_requests(self):
        """Create The dashboard of approvals."""
        models = self.env["ir.model"].search([("can_approve", "=", True)])
        approvals = []
        for model in models:
            approval_model = self.env["request.approval"].search(
                [("res_model_id", "=", model.id)]
            )
            if not approval_model:
                approval_model = self.env["request.approval"].create(
                    {"res_model_id": model.id}
                )
            approvals.append(approval_model.id)
        return {
            "name": _("Dashboard"),
            "view_type": "kanban",
            "view_mode": "kanban",
            "res_model": "request.approval",
            "view_id": False,
            "type": "ir.actions.act_window",
            "context": {"no_display_create": True},
            "domain": [("id", "in", approvals)],
        }
