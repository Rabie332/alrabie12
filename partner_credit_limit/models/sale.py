from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    credit_insurance_amount = fields.Monetary(
        string="Credit insurance amount",
    )
    total_open_invoices = fields.Monetary(
        string="Total open invoices",
    )
    show_credit_limit = fields.Boolean(
        string="Show Credit Limit",
    )

    @api.onchange("partner_id")
    def _onchange_partner(self):
        if self.partner_id:
            self.credit_insurance_amount = (
                self.partner_id.credit_insurance_limit_customer
            )
            self.total_open_invoices = self.partner_id.total_open_invoices_customer
            self.show_credit_limit = self.partner_id.show_credit_limit_customer

    @api.constrains("total_open_invoices", "credit_insurance_amount", "amount_total")
    def _check_credit_insurance(self):
        for sale in self:
            if (
                sale.show_credit_limit
                and (sale.amount_total + sale.total_open_invoices)
                > sale.credit_insurance_amount
            ):
                raise ValidationError(_("Total exceeds Credit limit"))
