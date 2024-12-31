from odoo import _, models
from odoo.exceptions import UserError


class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"

    def _check_cash_balance_end_real_same_as_computed(self):
        """Check the balance_end_real (encoded manually by the user) is equals to the
        balance_end (computed by odoo).
        For an atm statement, if there is a difference, the different is set
        automatically to a profit/loss account.
        If statement_atm_line_ids is empty: update balance_end_real.
        """
        bank_statements = self.filtered(
            lambda stmt: stmt.journal_type == "bank" and stmt.pos_session_id
        )
        for statement in bank_statements:
            if statement.pos_session_id.statement_atm_line_ids:
                if not statement.currency_id.is_zero(statement.difference):
                    st_line_vals = {
                        "statement_id": statement.id,
                        "journal_id": statement.journal_id.id,
                        "amount": statement.difference,
                        "date": statement.date,
                    }

                    if (
                        statement.currency_id.compare_amounts(statement.difference, 0.0)
                        < 0.0
                    ):
                        if not statement.journal_id.loss_account_id:
                            raise UserError(
                                _(
                                    "Please go on the %s journal and define a Loss Account. "
                                    "This account will be used to record ATM difference.",
                                    statement.journal_id.name,
                                )
                            )

                        st_line_vals["payment_ref"] = _(
                            "ATM difference observed during the counting (Loss)"
                        )
                        st_line_vals[
                            "counterpart_account_id"
                        ] = statement.journal_id.loss_account_id.id
                    else:
                        # statement.difference > 0.0
                        if not statement.journal_id.profit_account_id:
                            raise UserError(
                                _(
                                    "Please go on the %s journal and define a Profit Account. "
                                    "This account will be used to record ATM difference.",
                                    statement.journal_id.name,
                                )
                            )

                        st_line_vals["payment_ref"] = _(
                            "ATM difference observed during the counting (Profit)"
                        )
                        st_line_vals[
                            "counterpart_account_id"
                        ] = statement.journal_id.profit_account_id.id

                    self.env["account.bank.statement.line"].with_context(
                        check_move_validity=False
                    ).create(st_line_vals)
            else:
                statement.write({"balance_end_real": statement.balance_end})

        return super(
            AccountBankStatement, self
        )._check_cash_balance_end_real_same_as_computed()
