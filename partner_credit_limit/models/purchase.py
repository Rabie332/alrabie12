from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    credit_insurance_amount = fields.Monetary(
        string="Credit insurance limit",
    )
    total_open_invoices = fields.Monetary(
        string="Total open invoices",
    )
    show_credit_limit = fields.Boolean(
        string="Show Credit Limit Supplier",
    )

    @api.onchange("partner_id")
    def _onchange_partner(self):
        if self.partner_id:
            self.credit_insurance_amount = (
                self.partner_id.credit_insurance_limit_supplier
            )
            self.total_open_invoices = self.partner_id.total_open_invoices_supplier
            self.show_credit_limit = self.partner_id.show_credit_limit_supplier

    @api.constrains(
        "total_open_invoices",
        "credit_insurance_amount",
        "amount_total",
        "show_credit_limit",
    )
    def _check_credit_insurance(self):
        for purchase in self:
            if (
                purchase.show_credit_limit
                and (purchase.amount_total + purchase.total_open_invoices)
                > purchase.credit_insurance_amount
            ):
                raise ValidationError(_("Total exceeds Credit limit"))
