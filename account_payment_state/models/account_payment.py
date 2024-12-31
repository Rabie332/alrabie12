from odoo import _, fields, models
from odoo.exceptions import UserError


class AccountPayment(models.Model):
    _inherit = "account.payment"

    confirm_user_id = fields.Many2one("res.users", string="Confirm User")
    date_validate = fields.Date(string="Validate Date")
    display_buttons = fields.Boolean(
        string="display buttons", compute="_compute_display_button"
    )

    def action_review_payments(self):
        """Review several payments form the tree view."""
        payments = [payment for payment in self if payment.state == "draft"]
        if not payments:
            raise UserError(_("There are no payment in the draft state to review."))
        for payment in payments:
            payment.action_review()

    def action_reviewed_payments(self):
        """Put several payments under review form the tree view."""
        payments = [payment for payment in self if payment.state == "under_review"]
        if not payments:
            raise UserError(_("There are no payment under review to reviewed."))
        for payment in payments:
            payment.action_reviewed()

    def action_confirm_payments(self):
        """Confirm several payments under review form the tree view."""
        payments = [payment for payment in self if payment.state == "reviewed"]
        if not payments:
            raise UserError(_("There are no reviewed payment to confirm."))
        for payment in payments:
            payment.action_confirmed()

    def action_post_payment(self):
        """Post several payments under review form the tree view."""
        payments = [payment for payment in self if payment.state == "confirm"]
        if not payments:
            raise UserError(_("There are no confirmed payment to post."))
        for payment in payments:
            payment.action_post()

    def action_review(self):
        for rec in self:
            if rec.state == "draft":
                rec.state = "under_review"

    def action_reviewed(self):
        for rec in self:
            if rec.state == "under_review":
                rec.state = "reviewed"

    def action_confirmed(self):
        for rec in self:
            if rec.state == "reviewed":
                rec.state = "confirm"
                rec.confirm_user_id = rec.env.user

    def action_post(self):
        for payment in self:
            super(AccountPayment, payment).action_post()
            payment.date_validate = fields.Date.today()

    def _compute_display_button(self):
        for rec in self:
            rec.display_buttons = False
            if rec.user_has_groups("account_state.group_account_confirm_user") and (
                rec.state == "reviewed"
            ):
                rec.display_buttons = True
            if rec.user_has_groups("account_state.group_account_reviewer") and (
                rec.state == "under_review"
            ):
                rec.display_buttons = True
            if rec.user_has_groups("account.group_account_manager") and (
                rec.state in ["confirm", "posted"]
            ):
                rec.display_buttons = True
