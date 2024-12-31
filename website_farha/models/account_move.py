from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    attachment_ids = fields.Many2many(
        "ir.attachment", string="Attachments", compute="_compute_attachment"
    )

    def _compute_attachment(self):
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
            attachment_ids = (
                move.env["ir.attachment"]
                .search(
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
                .ids
            )
            move.write({"attachment_ids": [(6, 0, attachment_ids)]})
