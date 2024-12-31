from odoo import models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    def action_post(self):
        res = super(AccountPayment, self).action_post()
        hr_payment_request = self.env["hr.payment.request"].search(
            [("payment_id", "=", self.id)]
        )
        if hr_payment_request:
            hr_payment_request.is_paid = True
        return res
