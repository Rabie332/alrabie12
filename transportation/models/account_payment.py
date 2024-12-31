from lxml import etree

from odoo import _, api, fields, models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    shipping_order_id = fields.Many2one("shipping.order", string="Shipping Order")
    is_reward_drivers = fields.Boolean(string="Reward Drivers")
    shipping_line_ids = fields.Many2many("shipping.order.line", string="Shipping Lines")
    residual_reward = fields.Monetary(
        "Residual Reward", compute="_compute_residual_reward", compute_sudo=True
    )
    reward = fields.Monetary(
        string="Reward",
    )
    shipping_order_number = fields.Char(
        "Shipping Order Number", related="shipping_order_id.name"
    )

    # ------------------------------------------------------
    # ORM Methods
    # ------------------------------------------------------

    @api.model
    def fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        """fields_view_get to remove create from account payment."""
        res = super(AccountPayment, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu
        )
        if (
            self.env.context.get("default_is_reward_drivers")
            or self.env.context.get("clearance_request_state") == "close"
            or self.env.context.get("no_display_create")
        ):
            doc = etree.XML(res["arch"])
            for node in doc.xpath("//tree"):
                node.set("create", "0")
            for node in doc.xpath("//form"):
                node.set("create", "0")
            if self.env.context.get("clearance_request_state") == "close":
                for node in doc.xpath("//tree"):
                    node.set("edit", "0")
                    node.set("delete", "0")
                for node in doc.xpath("//form"):
                    node.set("delete", "0")
            res["arch"] = etree.tostring(doc, encoding="unicode")
        return res

    @api.model
    def create(self, vals):
        """Add employee number by company."""
        payment = super(AccountPayment, self).create(vals)
        if self._context.get("default_payment_fees"):
            payment.clearance_request_id.payment_fees_id = payment.id
        if self._context.get("default_payment_fees_statement"):
            payment.clearance_request_id.payment_fees_statement_id = payment.id
        if self._context.get("default_payment_fees_customs_id"):
            customs_payment = self.env["clearance.request.customs.payment"].browse(
                int(self._context.get("default_payment_fees_customs_id"))
            )
            customs_payment.payment_customs_id = payment.id
        return payment

    # ------------------------------------------------------
    # Compute Methods
    # ------------------------------------------------------
    @api.depends(
        "reward",
        "amount",
    )
    def _compute_residual_reward(self):
        """Calculate Residual Reward Amount."""
        for payment in self:
            payment.residual_reward = payment.reward - payment.amount
        # ------------------------------------------------------------
        # Business methods
        # ------------------------------------------------------------

    @api.model
    def get_drivers_rewards(self):
        """Create The dashboard of approvals."""
        payments = []
        view_id = (
            self.sudo()
            .env.ref("transportation.view_account_payment_tree_reward_transportation")
            .id,
        )
        employee = self.env["hr.employee"].search([("user_id", "=", self.env.user.id)])
        if employee:
            payments = (
                self.env["account.payment"]
                .sudo()
                .search(
                    [
                        ("is_reward_drivers", "=", True),
                        ("partner_id", "=", employee.address_home_id.id),
                    ]
                )
                .ids
            )
        return {
            "name": _("My Rewards"),
            "type": "ir.actions.act_window",
            "res_model": "account.payment",
            "view_mode": "tree",
            "views": [(view_id, "tree")],
            "view_id": False,
            "context": {"no_display_create": True},
            "domain": [("id", "in", payments)],
        }

    @api.model
    def get_payment_covenant(self):
        """Get the payment related to a covenant"""
        journal_ids = (
            self.env["transportation.financial.settings"]
            .search([("company_id", "=", self.env.company.id)])
            .mapped("journal_id")
            .ids
        )
        return {
            "name": _("Payments Covenant"),
            "view_mode": "tree,form",
            "res_model": "account.payment",
            "view_id": False,
            "type": "ir.actions.act_window",
            "context": {
                "default_journal_id": journal_ids[0] if journal_ids else False,
                "default_partner_type": "supplier",
                "default_payment_type": "outbound",
            },
            "domain": [
                ("journal_id", "in", journal_ids),
                ("is_reward_drivers", "=", False),
            ],
        }
