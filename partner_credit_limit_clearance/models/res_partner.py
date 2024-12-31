from odoo import models


class Partner(models.Model):
    _inherit = "res.partner"

    def _compute_total_open_invoices(self):
        """Calculate total open invoice customer and  supplier."""
        all_partners_and_children = {}
        all_partner_ids = []
        for partner in self:
            all_partners_and_children[partner] = (
                partner.with_context(active_test=False)
                .search([("id", "child_of", partner.id)])
                .ids
            )
            all_partner_ids += all_partners_and_children[partner]
            domain = [
                ("partner_id", "=", partner.id),
                ("state", "!=", "cancel"),
                ("payment_state", "in", ["not_paid", "partial"]),
            ]
            # calculate total open invoices customer
            partner.total_open_invoices_customer = sum(
                self.env["account.move"]
                .search(domain + [("move_type", "=", "out_invoice")])
                .mapped("amount_total")
            )
            # calculate total open invoices supplier
            partner.total_open_invoices_supplier = sum(
                self.env["account.move"]
                .search(domain + [("move_type", "=", "in_invoice")])
                .mapped("amount_total")
            )
