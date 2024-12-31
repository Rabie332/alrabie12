# Copyright 2021 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, models
from odoo.exceptions import AccessError, UserError


class PosSession(models.Model):
    _inherit = "pos.session"

    def _accumulate_amounts(self, data):
        data = super()._accumulate_amounts(data)
        # IDEA : move split_receivables and combine_receivables to
        # split_receivables_cash and combine_receivables_cash
        # if bank_statement is true on pos.payment.method
        # The big advantage of this implementation is that
        # there is no need to re-implement the logic of
        # _create_cash_statement_lines_and_cash_move_lines()
        # and update _reconcile_account_move_lines()
        # The drawback is that we store the bank journal for the non
        # cash method payment in the native field cash_journal_id
        # which is a bit "strange"
        # I have to do that because the method
        # _create_cash_statement_lines_and_cash_move_lines()
        # reads payment_method_id.cash_journal_id
        payment_methods_bank_statement = self.config_id.payment_method_ids.filtered(
            lambda payment_method: (
                not payment_method.is_cash_count
                and payment_method.bank_statement
                and payment_method.cash_journal_id
            )
        )
        if payment_methods_bank_statement:
            for pay_method in payment_methods_bank_statement:
                if pay_method.cash_journal_id not in self.statement_ids.mapped(
                    "journal_id"
                ):
                    self.write(
                        {
                            "statement_ids": [
                                (
                                    0,
                                    0,
                                    {
                                        "journal_id": pay_method.cash_journal_id.id,
                                        "name": self.name,
                                    },
                                )
                            ]
                        }
                    )
            # I can't pop data['split_receivables'] inside a loop on
            # data['split_receivables'],
            # that's why I use dict(data['split_receivables'])
            for pos_payment, value in dict(data["split_receivables"]).items():
                if pos_payment.payment_method_id in payment_methods_bank_statement:
                    data["split_receivables_cash"][pos_payment] = value
                    data["split_receivables"].pop(pos_payment)
            for pos_payment_method, value in dict(data["combine_receivables"]).items():
                if pos_payment_method in payment_methods_bank_statement:
                    data["combine_receivables_cash"][pos_payment_method] = value
                    data["combine_receivables"].pop(pos_payment_method)
        return data

    def _validate_session(self):
        """Remove savepoint which was added in Mars - 2023"""
        self.ensure_one()
        sudo = self.user_has_groups("point_of_sale.group_pos_user")
        if self.order_ids or self.statement_ids.line_ids:
            self.cash_real_transaction = self.cash_register_total_entry_encoding
            self.cash_real_expected = self.cash_register_balance_end
            self.cash_real_difference = self.cash_register_difference
            if self.state == "closed":
                raise UserError(_("This session is already closed."))
            self._check_if_no_draft_orders()
            self._check_invoices_are_posted()
            if self.update_stock_at_closing:
                self._create_picking_at_end_of_session()
            # Users without any accounting rights won't be able to create
            # the journal entry. If this case, switch to sudo for creation and posting.
            try:
                # Start patch
                # with self.env.cr.savepoint():
                # End Patch
                self.with_company(self.company_id)._create_account_move()
            except AccessError as e:
                if sudo:
                    self.sudo().with_company(self.company_id)._create_account_move()
                else:
                    raise e
            if self.move_id.line_ids:
                # Set the uninvoiced orders' state to 'done'
                self.env["pos.order"].search(
                    [("session_id", "=", self.id), ("state", "=", "paid")]
                ).write({"state": "done"})
            else:
                self.move_id.sudo().unlink()
        else:
            statement = self.cash_register_id
            if not self.config_id.cash_control:
                statement.write({"balance_end_real": statement.balance_end})
            statement.button_post()
            statement.button_validate()
        self.write({"state": "closed"})
        return {
            "type": "ir.actions.client",
            "name": "Point of Sale Menu",
            "tag": "reload",
            "params": {"menu_id": self.env.ref("point_of_sale.menu_point_root").id},
        }
