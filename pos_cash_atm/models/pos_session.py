from datetime import date, datetime

import pytz
from pytz import timezone

from odoo import _, api, fields, models


class PosSession(models.Model):
    _inherit = "pos.session"

    history_ids = fields.One2many("pos.session.history", "session_id", string="History")
    cash = fields.Monetary(string="Cash", compute="_compute_history_cash_atm", store=1)
    atm = fields.Monetary(string="ATM", compute="_compute_history_cash_atm", store=1)
    cash_register_balance_end_real = fields.Monetary(
        compute="_compute_history_cash_atm", store=1, related=False
    )
    system_cash = fields.Monetary(
        string="Cash (System)", compute="_compute_system_cash"
    )

    @api.depends("cash_real_expected")
    def _compute_system_cash(self):
        """Calculate the expected cash which changes after closing session."""
        for session in self:
            if session.cash_real_expected:
                session.system_cash = session.cash_real_expected
            else:
                session.system_cash = session.cash_register_balance_end

    def update_end_balance(self):
        """Recalculate End Balance Statement"""
        self.cash_real_expected = (
            self.cash_register_balance_start + self.cash_real_transaction
        )
        self.cash_real_difference = (
            self.cash_register_balance_end_real - self.cash_real_expected
        )
        self.cash_register_id._end_balance()

    # flake8: noqa: C901
    def update_cash_statement(self):
        if self.cash_register_id:
            self.cash_real_expected = (
                self.cash_register_balance_start + self.cash_real_transaction
            )
            self.cash_real_difference = (
                self.cash_register_balance_end_real - self.cash_real_expected
            )
            amount = 0
            if not self.cash_real_difference:
                # Calculate amount if difference 0
                amount = (
                    self.cash_register_id.balance_end_real
                    - self.cash_register_id.balance_start
                )
            # Calculate amount if difference less than 0
            if self.cash_real_difference < 0.0:
                amount = (
                    self.cash_register_id.balance_end_real
                    + abs(self.cash_real_difference)
                ) - self.cash_register_id.balance_start
                line_loss = self.cash_register_id.line_ids.filtered(
                    lambda line: line.payment_ref != self.name and line.amount < 0
                )
                if line_loss:
                    self.env.cr.execute(
                        "UPDATE account_bank_statement_line SET amount=%s WHERE id=%s",
                        (self.cash_real_difference, line_loss.id),
                    )
                else:
                    self.cash_register_id.with_context(
                        check_move_validity=False
                    )._check_balance_end_real_same_as_computed()
            # Calculate amount if difference grater than 0
            if self.cash_real_difference > 0.0:
                amount = (
                    self.cash_register_id.balance_end_real
                    - self.cash_register_id.balance_start
                ) - self.cash_real_difference
                line_profit = self.cash_register_id.line_ids.filtered(
                    lambda line: line.payment_ref != self.name and line.amount > 0
                )
                if line_profit:
                    self.env.cr.execute(
                        "UPDATE account_bank_statement_line SET amount=%s WHERE id=%s",
                        (self.cash_real_difference, line_profit.id),
                    )
                else:
                    self.cash_register_id.with_context(
                        check_move_validity=False
                    )._check_balance_end_real_same_as_computed()
            # Update value of statement line pos
            self.env.cr.execute(
                "UPDATE account_bank_statement_line SET amount=%s WHERE id=%s",
                (
                    amount,
                    self.cash_register_id.line_ids.filtered(
                        lambda line: line.payment_ref == self.name
                    ).id,
                ),
            )
            self.cash_register_id._end_balance()
            # Update value of move and reconcile of pos
            for move_line in self.move_id.line_ids:
                if move_line.name == self.name:
                    if move_line.debit:
                        self.env.cr.execute(
                            "UPDATE account_move_line SET debit=%s WHERE id=%s",
                            (amount, move_line.id),
                        )
                    if move_line.credit:
                        self.env.cr.execute(
                            "UPDATE account_move_line SET credit=%s WHERE id=%s",
                            (amount, move_line.id),
                        )
                    if move_line.full_reconcile_id:
                        for (
                            line_reconcile
                        ) in move_line.full_reconcile_id.reconciled_line_ids:
                            if line_reconcile.debit:
                                self.env.cr.execute(
                                    "UPDATE account_move_line SET debit=%s WHERE id=%s",
                                    (amount, line_reconcile.id),
                                )
                            if line_reconcile.credit:
                                self.env.cr.execute(
                                    "UPDATE account_move_line SET credit=%s WHERE id=%s",
                                    (amount, line_reconcile.id),
                                )
            # Update value of move for diffrences
            for move_loss_profit_line in self.cash_register_id.line_ids.filtered(
                lambda line: line.payment_ref != self.name
            ).mapped("move_id.line_ids"):
                if move_loss_profit_line.debit:
                    self.env.cr.execute(
                        "UPDATE account_move_line SET debit=%s, amount_currency=%s WHERE id=%s",
                        (
                            abs(self.cash_real_difference),
                            abs(self.cash_real_difference),
                            move_loss_profit_line.id,
                        ),
                    )

                if move_loss_profit_line.credit:
                    # flake8: noqa: B950
                    self.env.cr.execute(
                        "UPDATE account_move_line SET credit=%s, amount_currency=%s WHERE id=%s",
                        (
                            abs(float(self.cash_real_difference)),
                            -1 * abs(self.cash_real_difference),
                            move_loss_profit_line.id,
                        ),
                    )

    def _validate_session(self):
        """Validate session."""
        context = self._context.copy()
        context.update({"pos_session_id": self.id})
        res = super(PosSession, self.with_context(context))._validate_session()
        vals = {}
        # Add date start and date end
        if not self.start_at:
            vals["start_at"] = fields.Datetime.now()
        if not self.stop_at:
            vals["stop_at"] = fields.Datetime.now()
        if vals:
            self.write(vals)
        return res

    def force_action_pos_session_close(self):
        """Validate session."""
        for session in self:
            session.env["account.bank.statement.cashbox"].create(
                [
                    {
                        "start_bank_stmt_ids": [],
                        "end_bank_stmt_ids": [
                            (
                                4,
                                session.cash_register_id.id,
                            )
                        ],
                        "cashbox_lines_ids": [
                            (0, 0, {"number": 1, "coin_value": session.cash})
                        ],
                    }
                ]
            )
            session._validate_session()
        return True

    def update_cash_session(self, cash, atm):
        """add cash or atm to history of session."""
        expected_atm = 0
        expected_cash = self.cash_register_balance_start
        bank_payment_methods = self.payment_method_ids.filtered(
            lambda m: not m.is_cash_count
        )
        cash_payment_methods = self.payment_method_ids.filtered(
            lambda m: m.is_cash_count
        )
        if bank_payment_methods:
            atm_result = self.env["pos.payment"].read_group(
                [
                    ("session_id", "=", self.id),
                    ("payment_method_id", "in", bank_payment_methods.ids),
                ],
                ["amount"],
                ["session_id"],
            )
            if atm_result:
                expected_atm = atm_result[0]["amount"]
        if cash_payment_methods:
            cash_result = self.env["pos.payment"].read_group(
                [
                    ("session_id", "=", self.id),
                    ("payment_method_id", "in", cash_payment_methods.ids),
                ],
                ["amount"],
                ["session_id"],
            )
            if cash_result:
                expected_cash += cash_result[0]["amount"]
        line_history = self.env["pos.session.history"].new(
            {
                "cash": cash,
                "atm": atm,
                "expected_atm": expected_atm,
                "expected_cash": expected_cash,
            }
        )

        self.history_ids += line_history

    def get_state(self):
        """Get state."""
        return self.state

    @api.depends(
        "history_ids",
        "history_ids.cash",
        "history_ids.atm",
        "cash_register_id.balance_end_real",
    )
    def _compute_history_cash_atm(self):
        """Calculate total cash and atm."""
        for session in self:
            # N.b Cashier counts all session sales (his sales + previous checkouts
            # sales)
            last_line = False
            atm = cash = 0.0
            if self.history_ids:
                last_line = self.history_ids.sorted(key=lambda h: h.create_date)[-1]
            if last_line:
                cash = last_line.cash
                atm = last_line.atm

            session.cash = cash
            session.atm = atm
            if session.cash_register_id.balance_end_real:
                session.cash_register_balance_end_real = (
                    session.cash_register_id.balance_end_real
                )
            else:
                session.cash_register_balance_end_real = cash

    def get_current_date(self):
        if self.env.user and self.env.user.tz:
            tz = self.env.user.tz
            tz = timezone(tz)
        else:
            tz = pytz.utc
        if tz:
            date_timezone = datetime.now(tz)
            return date_timezone.strftime("%d/%m/%Y")
        else:
            return date.today().strftime("%d/%m/%Y")

    def get_current_time(self):
        if self.env.user and self.env.user.tz:
            tz = self.env.user.tz
            tz = timezone(tz)
        else:
            tz = pytz.utc
        if tz:
            date_timezone = datetime.now(tz)
            return date_timezone.strftime("%I:%M %p")
        else:
            return datetime.now().strftime("%I:%M:%S %p")

    def get_total_sales(self):
        total_price = 0.0
        for line in self.order_ids.filtered(
            lambda order: order.amount_paid >= 0
        ).mapped("lines"):
            total_price += line.qty * line.price_unit
        return total_price

    def get_total_reversal(self):
        total_price = sum(
            self.order_ids.filtered(lambda order: order.amount_paid <= 0).mapped(
                "amount_paid"
            )
        )
        return total_price

    def get_reversal_orders_detail(self):
        reversal_orders_detail = {}
        for order in self.order_ids.filtered(lambda order: order.amount_paid <= 0):
            reversal_orders_detail[order.name] = []
            for line in order.lines:
                reversal_orders_detail[order.name].append(
                    {
                        "product_id": line.product_id.display_name,
                        "qty": line.qty,
                        "price_subtotal_incl": line.price_subtotal_incl,
                    }
                )
        return reversal_orders_detail

    def get_total_tax(self):
        total_tax = sum(self.order_ids.mapped("amount_tax"))
        return total_tax

    def get_vat_tax(self):
        taxes_info = []
        tax_list = (
            self.order_ids.mapped("lines")
            .filtered(lambda line: line.tax_ids_after_fiscal_position)
            .mapped("tax_ids_after_fiscal_position")
            .ids
        )
        for tax in self.env["account.tax"].browse(tax_list):
            total_tax = 0.00
            net_total = 0.00
            for line in (
                self.env["pos.order.line"]
                .search([("order_id", "in", [order.id for order in self.order_ids])])
                .filtered(lambda line: tax in line.tax_ids_after_fiscal_position)
            ):
                total_tax += line.price_subtotal * tax.amount / 100
                net_total += line.price_subtotal
            taxes_info.append(
                {
                    "tax_name": tax.name,
                    "tax_total": total_tax,
                    "tax_per": tax.amount,
                    "net_total": net_total,
                    "gross_tax": total_tax + net_total,
                }
            )
        return taxes_info

    def get_total_discount(self):
        total_discount = 0.0
        for line in self.order_ids.mapped("lines"):
            total_discount += (line.qty * line.price_unit * line.discount) / 100
        return total_discount

    def get_sale_summary_by_user(self):
        user_summary = {}
        for line in self.order_ids.mapped("lines"):
            if not user_summary.get(line.create_uid.name, None):
                user_summary[line.create_uid.name] = line.price_subtotal_incl
            else:
                user_summary[line.create_uid.name] += line.price_subtotal_incl
        return user_summary

    def get_total_refund(self):
        refund_total = sum(
            self.order_ids.filtered(lambda order: order.amount_total < 0).mapped(
                "amount_total"
            )
        )
        return refund_total

    def get_total_first(self):
        return sum(order.amount_total for order in self.order_ids)

    def get_gross_total(self):
        gross_total = 0.0
        for line in self.order_ids.mapped("lines"):
            gross_total += line.qty * (line.price_unit - line.product_id.standard_price)
        return gross_total

    def get_net_gross_total(self):
        net_gross_profit = self.get_gross_total() - self.get_total_tax()
        return net_gross_profit

    def get_payments(self):
        statement_line_obj = self.env["account.bank.statement.line"]
        pos_order_obj = self.env["pos.order"]
        pos_ids = pos_order_obj.search(
            [
                ("state", "in", ["paid", "invoiced", "done"]),
                ("company_id", "=", self.env.user.company_id.id),
                ("session_id", "=", self.id),
            ]
        )
        if pos_ids:
            statement_line_ids = statement_line_obj.search(
                [("pos_statement_id", "in", pos_ids.ids)]
            )
            if statement_line_ids:
                self._cr.execute(
                    "select aj.name,sum(amount) from account_bank_statement_line as "
                    "absl,account_bank_statement as abs,account_journal as aj "
                    "where absl.statement_id = abs.id and abs.journal_id = aj.id  "
                    "and absl.id IN %s "
                    "group by aj.name ",
                    (tuple(statement_line_ids.ids)),
                )

                data = self._cr.dictfetchall()
                return data
        else:
            return {}

    def get_payments_amount(self):
        payments_amount = []
        for payment_method in self.config_id.payment_method_ids:
            payments = self.env["pos.payment"].search(
                [
                    ("session_id", "=", self.id),
                    ("payment_method_id", "=", payment_method.id),
                ]
            )
            journal_dict = {"name": payment_method.name, "amount": 0}
            for payment in payments:
                amount = payment.amount
                journal_dict["amount"] += amount
            payments_amount.append(journal_dict)
        return payments_amount

    def get_total_closing(self):
        return self.cash_register_balance_end_real

    def get_cash_in(self):
        values = []
        account_bank_statement_lines = self.env["account.bank.statement.line"].search(
            [("statement_id.pos_session_id", "=", self.id), ("amount", ">", 0)]
        )
        for line in account_bank_statement_lines:
            values.append({"amount": line.amount, "date": line.create_date})
        return values

    def get_cash_out(self):
        values = []
        account_bank_statement_lines = self.env["account.bank.statement.line"].search(
            [("statement_id.pos_session_id", "=", self.id), ("amount", "<", 0)]
        )
        for line in account_bank_statement_lines:
            values.append({"amount": line.amount, "date": line.create_date})
        return values

    def build_sessions_report(self):
        vals = {}
        session_state = {
            "new_session": _("New Session"),
            "opening_control": _("Opening Control"),
            "opened": _("In Progress"),
            "closing_control": _("Closing Control"),
            "closed": _("Closed & Posted"),
        }
        for session in self:
            session_report = {}
            session_report["session"] = self.sudo().search_read(
                [("id", "=", session.id)], []
            )[0]
            session_report["name"] = session.name
            session_report["current_date"] = session.get_current_date()
            session_report["current_time"] = session.get_current_time()
            session_report["state"] = session_state[session.state]
            session_report["start_at"] = session.start_at
            session_report["stop_at"] = session.stop_at
            session_report["seller"] = session.user_id.name
            session_report[
                "cash_register_balance_start"
            ] = session.cash_register_balance_start
            session_report["sales_total"] = session.get_total_sales()
            session_report["reversal_total"] = session.get_total_reversal()
            session_report[
                "reversal_orders_detail"
            ] = session.get_reversal_orders_detail()
            session_report["taxes"] = session.get_vat_tax()
            session_report["taxes_total"] = session.get_vat_tax()
            session_report["discounts_total"] = session.get_total_discount()
            session_report["users_summary"] = session.get_sale_summary_by_user()
            session_report["refund_total"] = session.get_total_refund()
            session_report["gross_total"] = session.get_total_first()
            session_report["gross_profit_total"] = session.get_gross_total()
            session_report["net_gross_total"] = session.get_net_gross_total()
            session_report[
                "cash_register_balance_end"
            ] = session.cash_register_balance_end
            session_report["closing_total"] = session.get_total_closing()
            session_report["payments_amount"] = session.get_payments_amount()
            session_report["cashs_in"] = session.get_cash_in()
            session_report["cashs_out"] = session.get_cash_out()
            vals[session.id] = session_report
        return vals


class PosSessionHistory(models.Model):
    _name = "pos.session.history"
    _description = "Session History"

    session_id = fields.Many2one("pos.session", string="Session")
    cash = fields.Float(string="Cash (Cashier)")
    atm = fields.Float(string="ATM (Cashier)")
    expected_cash = fields.Float(string="Cash (System)")
    expected_atm = fields.Float(string="ATM (System)")
    checkout_cash = fields.Float(
        string="Checkout cash", compute="_compute_last_checkout_sales"
    )
    checkout_atm = fields.Float(
        string="Checkout ATM", compute="_compute_last_checkout_sales"
    )

    @api.depends("cash", "atm", "expected_cash", "expected_atm")
    def _compute_last_checkout_sales(self):
        """Calculate difference between current sales and the last checkout."""
        for history in self:
            last_checkout_atm = last_checkout_cash = 0.0
            last_line = self.env["pos.session.history"].search(
                [
                    ("session_id", "=", history.session_id.id),
                    ("create_date", "<", history.create_date),
                ],
                order="create_date desc",
                limit=1,
            )
            if last_line:
                last_checkout_cash = last_line.cash
                last_checkout_atm = last_line.atm

            history.checkout_cash = history.cash - last_checkout_cash
            history.checkout_atm = history.atm - last_checkout_atm
