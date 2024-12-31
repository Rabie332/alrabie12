from odoo import api, fields, models


class PosSession(models.Model):
    _inherit = "pos.session"

    bank_register_balance_end = fields.Monetary(
        compute="_compute_bank_balance",
        string="ATM Theoretical Closing Balance",
        readonly=True,
    )
    bank_register_difference = fields.Monetary(
        string="ATM before Closing Difference", readonly=True
    )
    statement_atm_line_ids = fields.One2many(
        "atm.statement.line",
        "session_id",
        string="ATM statement lines",
    )

    def _check_pos_session_balance(self):
        for session in self:
            for statement in session.statement_ids:
                if statement.journal_type == "cash":
                    if (statement != session.cash_register_id) and (
                        statement.balance_end != statement.balance_end_real
                    ):
                        statement.write({"balance_end_real": statement.balance_end})
                elif statement.journal_type == "bank":
                    for atm_line in session.statement_atm_line_ids:
                        if (
                            atm_line.payment_method_id.cash_journal_id
                            == statement.journal_id
                        ):
                            statement.write(
                                {
                                    "balance_end_real": statement.balance_start
                                    + atm_line.amount
                                }
                            )

    @api.depends(
        "payment_method_ids", "order_ids.payment_ids.amount", "statement_atm_line_ids"
    )
    def _compute_bank_balance(self):
        for session in self:
            bank_payment_methods = session.payment_method_ids.filtered(
                lambda m: not m.is_cash_count
            )
            if bank_payment_methods:
                total_bank_payment = 0.0
                result = self.env["pos.payment"].read_group(
                    [
                        ("session_id", "=", session.id),
                        ("payment_method_id", "in", bank_payment_methods.ids),
                    ],
                    ["amount"],
                    ["session_id"],
                )
                if result:
                    total_bank_payment = result[0]["amount"]
                session.bank_register_balance_end = total_bank_payment
                statement_lines_amount = sum(
                    session.statement_atm_line_ids.mapped("amount")
                )
                session.bank_register_difference = (
                    statement_lines_amount - total_bank_payment
                )
            else:
                session.bank_register_balance_end = 0.0

    @api.model
    def create(self, values):
        res = super(PosSession, self).create(values)
        if self.user_has_groups("point_of_sale.group_pos_user"):
            res = res.sudo()
        payment_methods_bank_statement = res.config_id.payment_method_ids.filtered(
            lambda payment_method: (
                not payment_method.is_cash_count
                and payment_method.bank_statement
                and payment_method.cash_journal_id
            )
        )
        if payment_methods_bank_statement:
            res.write(
                {
                    "statement_ids": [
                        (
                            0,
                            0,
                            {
                                "journal_id": pay_method.cash_journal_id.id,
                                "name": res.name,
                            },
                        )
                        for pay_method in payment_methods_bank_statement
                    ]
                }
            )
        return res
