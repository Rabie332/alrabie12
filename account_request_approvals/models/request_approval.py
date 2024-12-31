from odoo import _, api, fields, models
from odoo.osv import expression


class ResUsers(models.Model):
    _inherit = "res.users"

    # ------------------------------------------------------------
    # Business methods
    # ------------------------------------------------------------
    @api.model
    def get_approval_requests(self):
        """Create the dashboard of approvals."""
        self.ensure_one()
        models = self.env["ir.model"].search([("can_approve", "=", True)])
        approvals = []
        for model in models:
            approval_models = self.env["request.approval"].search(
                [("res_model_id", "=", model.id)]
            )
            if not approval_models:
                approval_model = self.env["request.approval"].create(
                    {"res_model_id": model.id}
                )
                approvals.append(approval_model.id)
                if approval_model and model.model == "account.move":
                    # create two approval objects for customer invoices and supplier invoices
                    # for out invoices
                    approval_model.write(
                        {"name": _("Customer Invoices"), "type": "out_invoice"}
                    )
                    # create one for in invoices
                    approval_out_invoice = self.env["request.approval"].create(
                        {"res_model_id": model.id}
                    )
                    approval_out_invoice.write(
                        {"name": _("Supplier Invoices"), "type": "in_invoice"}
                    )
                    approvals.append(approval_out_invoice.id)
            approvals.extend(approval_models.ids)
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


class RequestApproval(models.Model):
    _inherit = "request.approval"

    type = fields.Selection(
        [("out_invoice", "Out Invoice"), ("in_invoice", "In Invoice")], string="Type"
    )
    name = fields.Char(
        compute="_compute_name",
    )

    # ------------------------------------------------------------
    # Compute methods
    # ------------------------------------------------------------
    @api.depends("res_model_id", "type")
    def _compute_name(self):
        for approval in self:
            approval.name = approval.res_model_id.name
            if approval.res_model_id.model == "account.move":
                approval.name = (
                    _("Customer Invoices")
                    if approval.type == "out_invoice"
                    else _("Supplier Invoices")
                )

    # ------------------------------------------------------------
    # Business methods
    # ------------------------------------------------------------

    def get_activities(self):
        """Get requests to approve from my activities."""
        activities = (
            self.env["mail.activity"]
            .search(
                [
                    ("user_id", "=", self.env.user.id),
                    ("activity_type_id.category", "=", "validation"),
                    ("res_model_id", "=", self.res_model_id.id),
                ]
            )
            .mapped("res_id")
        )
        domain = [("id", "in", activities)]
        if self.res_model_id.model == "account.move":
            domain = expression.AND([domain, [("move_type", "=", self.type)]])
        return self.env[self.res_model_id.model].search(domain)
