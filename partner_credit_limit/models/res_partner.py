from odoo import api, fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    credit_insurance_limit_customer = fields.Monetary(
        string="Credit insurance Limit Customer"
    )
    total_open_invoices_customer = fields.Monetary(
        string="Total open invoices Customer", compute="_compute_total_open_invoices"
    )
    credit_insurance_limit_supplier = fields.Monetary(
        string="Credit insurance limit Supplier"
    )
    total_open_invoices_supplier = fields.Monetary(
        string="Total open invoices Supplier", compute="_compute_total_open_invoices"
    )
    show_credit_limit_customer = fields.Boolean(string="Show Credit Limit Customer")
    show_credit_limit_supplier = fields.Boolean(string="Show Credit Limit Supplier")

    def _compute_total_open_invoices(self):
        all_partners_and_children = {}
        all_partner_ids = []
        for partner in self:
            all_partners_and_children[partner] = (
                self.with_context(active_test=False)
                .search([("id", "child_of", partner.id)])
                .ids
            )
            all_partner_ids += all_partners_and_children[partner]
            domain = [
                ("partner_id", "=", partner.id),
                ("state", "=", "posted"),
                ("payment_state", "in", ["not_paid", "partial"]),
            ]
            partner.total_open_invoices_customer = sum(
                self.env["account.move"]
                .search(domain + [("move_type", "=", "out_invoice")])
                .mapped("amount_residual")
            )
            partner.total_open_invoices_supplier = sum(
                self.env["account.move"]
                .search(domain + [("move_type", "=", "in_invoice")])
                .mapped("amount_residual")
            )

    @api.onchange("show_credit_limit_supplier")
    def _onchange_show_credit_limit_supplier(self):
        if not self.show_credit_limit_supplier:
            self.credit_insurance_limit_supplier = 0

    @api.onchange("show_credit_limit_customer")
    def _onchange_show_credit_limit_customer(self):
        if not self.show_credit_limit_customer:
            self.credit_insurance_limit_customer = 0
