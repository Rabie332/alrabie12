from lxml import etree

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    clearance_request_id = fields.Many2one(
        "clearance.request", string="Clearance Request"
    )
    date = fields.Date(tracking=True)
    attachment_count = fields.Integer(
        string="Attachments number",
        compute="_compute_attachment_count",
    )
    is_warehouse_invoice = fields.Boolean(string="Is warehouse invoice")

    # ------------------------------------------------------------
    # Compute methods
    # ------------------------------------------------------------

    def _compute_attachment_count(self):
        for move in self:
            payments = []
            if move.clearance_request_id:
                payments = (
                    move.env["account.payment"]
                    .search(
                        move.clearance_request_id._payment_domain()
                        + [("partner_type", "=", "supplier"), ("state", "!=", "cancel")]
                    )
                    .ids
                )
            move.attachment_count = move.env["ir.attachment"].search_count(
                [
                    "|",
                    "&",
                    ("res_model", "=", "account.payment"),
                    ("res_id", "in", payments),
                    "&",
                    ("res_model", "=", move._name),
                    ("res_id", "in", move.ids),
                ]
            )

    # ------------------------------------------------------
    # Orm Methods
    # ------------------------------------------------------
    @api.model
    def fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        """fields_view_get to remove create from account move."""
        res = super(AccountMove, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu
        )
        if self.env.context.get("default_payment_fees"):
            doc = etree.XML(res["arch"])
            for node in doc.xpath("//tree"):
                node.set("create", "0")
                node.set("edit", "0")
                node.set("delete", "0")
            for node in doc.xpath("//form"):
                node.set("create", "0")
                node.set("edit", "0")
                node.set("delete", "0")
            res["arch"] = etree.tostring(doc, encoding="unicode")
        return res

    # ------------------------------------------------------
    # Business Methods
    # ------------------------------------------------------

    def attachment_tree_view(self):
        """Get attachments for this object."""
        attachment_action = self.env.ref("base.action_attachment")
        action = attachment_action.sudo().read()[0]
        payments = []
        if self.clearance_request_id:
            payments = (
                self.env["account.payment"]
                .search(
                    self.clearance_request_id._payment_domain()
                    + [("partner_type", "=", "supplier"), ("state", "!=", "cancel")]
                )
                .ids
            )
        action["context"] = {
            "default_res_model": "account.move",
            "default_res_id": self.ids[0],
        }
        action["domain"] = str(
            [
                "|",
                "&",
                ("res_model", "=", "account.payment"),
                ("res_id", "in", payments),
                "&",
                ("res_model", "=", "account.move"),
                ("res_id", "in", self.ids),
            ]
        )
        return action
