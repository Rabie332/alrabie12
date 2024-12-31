from odoo import _, models


class AccountMove(models.Model):
    _inherit = "account.move"

    def send_whatsapp_message(self):
        total_taxes = 0
        for amount_by_group in self.amount_by_group:
            total_taxes += amount_by_group[1]
        message = _(
            """     Dear *{partner_name}*,%0a
Your Invoice *{invoice_name}* has been posted.%0a
*Invoice Date:{invoice_date}*,%0a
Due Date:*{invoice_date_due}*,%0a
Untaxed Amount:*{amount_untaxed} {currency}*,%0a
Taxes:*{total_taxes} {currency}*,%0a
Total Amount:*{amount_total} {currency}*,%0a
*Due Amount:{amount_residual} {currency}*,%0a
_Best regards_,%0a
*{user_name}* , *{company_name}*"""
        ).format(
            partner_name=self.partner_id.name,
            invoice_name=self.name,
            invoice_date=self.invoice_date,
            invoice_date_due=self.invoice_date_due,
            amount_untaxed=self.amount_untaxed,
            total_taxes=str(total_taxes),
            amount_total=self.amount_total,
            amount_residual=self.amount_residual,
            company_name=self.company_id.name,
            user_name=self.env.user.name,
            currency=self.currency_id.name,
        )
        return {
            "type": "ir.actions.act_window",
            "name": _("Send invoice by Whatsapp"),
            "res_model": "whatsapp.message.wizard",
            "target": "new",
            "view_mode": "form",
            "context": {
                "default_partner_id": self.partner_id.id,
                "default_mobile": self.partner_id.mobile,
                "default_message": message,
            },
        }
