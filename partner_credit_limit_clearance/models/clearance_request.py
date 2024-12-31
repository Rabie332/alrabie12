from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ClearanceRequest(models.Model):
    _inherit = "clearance.request"

    credit_insurance_amount = fields.Monetary(
        string="Credit insurance amount",
        related="partner_id.credit_insurance_limit_customer",
        store=1,
    )
    total_open_invoices = fields.Monetary(
        string="Total open invoices",
        related="partner_id.total_open_invoices_customer",
        store=1,
    )
    show_credit_limit = fields.Boolean(
        string="Show Credit Limit",
        related="partner_id.show_credit_limit_customer",
        store=1,
    )

    @api.onchange("partner_id")
    def _onchange_partner(self):
        if self.partner_id:
            self.credit_insurance_amount = (
                self.partner_id.credit_insurance_limit_customer
            )
            self.total_open_invoices = self.partner_id.total_open_invoices_customer
            self.show_credit_limit = self.partner_id.show_credit_limit_customer

    @api.constrains("total_open_invoices", "credit_insurance_amount")
    def _check_credit_insurance(self):
        for clearance in self:
            if (
                clearance.show_credit_limit
                and clearance.total_open_invoices > clearance.credit_insurance_amount
            ):
                raise ValidationError(_("Total open invoices exceeds Credit limit"))
