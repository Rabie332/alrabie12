from odoo import _, fields, models
from odoo.exceptions import ValidationError


class AccountPayment(models.Model):
    _inherit = "account.payment"

    active = fields.Boolean(string="Active", default=True)

    # ------------------------------------------------------
    # Business Methods
    # ------------------------------------------------------

    def toggle_active(self):
        for payment in self:
            if payment.state != "cancel":
                raise ValidationError(_("Only canceled payments can be archived"))
            payment.with_context(active_test=False).line_ids.filtered(
                lambda line: line.active == payment.active
            ).toggle_active()
        super(AccountPayment, self).toggle_active()
