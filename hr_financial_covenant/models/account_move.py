from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_post(self):
        for move in self:
            super(AccountMove, move).action_post()
            covenant = self.env["hr.financial.covenant"].search(
                [("account_move_id", "=", move.id)]
            )
            if covenant:
                covenant.is_paid = True
