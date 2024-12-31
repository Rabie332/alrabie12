from odoo import _, api, fields, models
from odoo.exceptions import UserError


class HrPayslipLine(models.Model):
    _inherit = "hr.payslip.line"

    def _get_partner_id(self, credit_account):
        """
        Get partner_id of slip line to use in account_move_line
        """
        # use partner of salary rule or fallback on employee's address
        register_partner_id = self.salary_rule_id.register_id.partner_id
        partner_id = (
            register_partner_id.id or self.slip_id.employee_id.address_home_id.id
        )
        if credit_account:
            if (
                register_partner_id
                or self.salary_rule_id.account_credit.internal_type
                in ("receivable", "payable")
            ):
                return partner_id
        else:
            if (
                register_partner_id
                or self.salary_rule_id.account_debit.internal_type
                in ("receivable", "payable")
            ):
                return partner_id
        return False


class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    date = fields.Date(
        "Date Account",
        states={"draft": [("readonly", False)]},
        readonly=True,
        help="Keep empty to use the period of the validation(Payslip) date.",
    )
    journal_id = fields.Many2one(
        "account.journal",
        "Salary Journal",
        readonly=True,
        required=True,
        states={"draft": [("readonly", False)]},
        default=lambda self: self.env["account.journal"].search(
            [("type", "=", "general")], limit=1
        ),
    )
    move_id = fields.Many2one(
        "account.move", "Accounting Entry", readonly=True, copy=False
    )

    @api.model
    def create(self, vals):
        if "journal_id" in self.env.context:
            vals["journal_id"] = self.env.context.get("journal_id")
        return super(HrPayslip, self).create(vals)

    @api.onchange("contract_id")
    def onchange_contract(self):
        super(HrPayslip, self).onchange_contract()
        self.journal_id = (
            self.payslip_run_id.journal_id.id
            or self.contract_id.journal_id.id
            or (not self.contract_id and self.default_get(["journal_id"])["journal_id"])
            or self.journal_id
        )

    def action_payslip_cancel(self):
        moves = self.mapped("move_id")
        moves.filtered(lambda x: x.state == "posted").button_cancel()
        moves.unlink()
        return super(HrPayslip, self).action_payslip_cancel()

    def get_lines(self, slip, date, journal_id):
        line_ids = []
        debit_sum = 0.0
        credit_sum = 0.0
        currency = slip.company_id.currency_id or journal_id.company_id.currency_id

        for line in slip.details_by_salary_rule_category:
            amount = currency.round(slip.credit_note and -line.total or line.total)
            if currency.is_zero(amount):
                continue
            debit_account_id = line.salary_rule_id.account_debit.id
            credit_account_id = line.salary_rule_id.account_credit.id

            if debit_account_id:
                debit_line = (
                    0,
                    0,
                    {
                        "name": line.name,
                        "partner_id": line._get_partner_id(credit_account=False),
                        "account_id": debit_account_id,
                        "journal_id": journal_id.id,
                        "date": date,
                        "debit": amount > 0.0 and amount or 0.0,
                        "credit": amount < 0.0 and -amount or 0.0,
                        "analytic_account_id": line.salary_rule_id.analytic_account_id.id
                        or slip.contract_id.analytic_account_id.id,
                        "tax_line_id": line.salary_rule_id.account_tax_id.id,
                    },
                )
                line_ids.append(debit_line)
                debit_sum += debit_line[2]["debit"] - debit_line[2]["credit"]

            if credit_account_id:
                credit_line = (
                    0,
                    0,
                    {
                        "name": line.name,
                        "partner_id": line._get_partner_id(credit_account=True),
                        "account_id": credit_account_id,
                        "journal_id": journal_id.id,
                        "date": date,
                        "debit": amount < 0.0 and -amount or 0.0,
                        "credit": amount > 0.0 and amount or 0.0,
                        "analytic_account_id": line.salary_rule_id.analytic_account_id.id
                        or slip.contract_id.analytic_account_id.id,
                        "tax_line_id": line.salary_rule_id.account_tax_id.id,
                    },
                )
                line_ids.append(credit_line)
                credit_sum += credit_line[2]["credit"] - credit_line[2]["debit"]

        if currency.compare_amounts(credit_sum, debit_sum) == -1:
            acc_id = journal_id.default_account_id.id
            if not acc_id:
                raise UserError(
                    _(
                        'The Expense Journal "%s" has not properly configured the '
                        "Credit Account!"
                    )
                    % (journal_id.name)
                )
            adjust_credit = (
                0,
                0,
                {
                    "name": _("Adjustment Entry"),
                    "partner_id": False,
                    "account_id": acc_id,
                    "journal_id": journal_id.id,
                    "date": date,
                    "debit": 0.0,
                    "credit": currency.round(debit_sum - credit_sum),
                },
            )
            line_ids.append(adjust_credit)

        elif currency.compare_amounts(debit_sum, credit_sum) == -1:
            acc_id = journal_id.default_account_id.id
            if not acc_id:
                raise UserError(
                    _(
                        'The Expense Journal "%s" has not properly configured the '
                        "Debit Account!"
                    )
                    % (journal_id.name)
                )
            adjust_debit = (
                0,
                0,
                {
                    "name": _("Adjustment Entry"),
                    "partner_id": False,
                    "account_id": acc_id,
                    "journal_id": journal_id.id,
                    "date": date,
                    "debit": currency.round(credit_sum - debit_sum),
                    "credit": 0.0,
                },
            )
            line_ids.append(adjust_debit)
        return line_ids

    def create_move(self, slip, move_dict, date):
        move = self.env["account.move"].create(move_dict)
        slip.write({"move_id": move.id, "date": date})
        move.post()

    def action_payslip_done(self):
        res = super(HrPayslip, self).action_payslip_done()
        for slip in self:
            date = slip.date or slip.date_to
            if not slip.company_id.is_payroll_account_batch and not slip.move_id:
                name = _("Payslip of %s") % (slip.employee_id.name)
                move_dict = {
                    "narration": name,
                    "ref": "%s %s" % (slip.employee_id.name, slip.number),
                    "journal_id": slip.journal_id.id,
                    "date": slip.date or slip.date_to,
                }
                move_dict["line_ids"] = self.get_lines(slip, date, slip.journal_id)
                self.create_move(slip, move_dict, date)
        return res


class HrSalaryRule(models.Model):
    _inherit = "hr.salary.rule"

    analytic_account_id = fields.Many2one(
        "account.analytic.account", "Analytic Account", company_dependent=True
    )
    account_tax_id = fields.Many2one("account.tax", "Tax")
    account_debit = fields.Many2one(
        "account.account",
        "Debit Account",
        company_dependent=True,
        domain=[("deprecated", "=", False)],
    )
    account_credit = fields.Many2one(
        "account.account",
        "Credit Account",
        company_dependent=True,
        domain=[("deprecated", "=", False)],
    )


class HrContract(models.Model):
    _inherit = "hr.contract"
    _description = "Employee Contract"

    analytic_account_id = fields.Many2one(
        "account.analytic.account", "Analytic Account"
    )
    journal_id = fields.Many2one("account.journal", "Salary Journal")


class HrPayslipRun(models.Model):
    _inherit = "hr.payslip.run"

    journal_id = fields.Many2one(
        "account.journal",
        "Salary Journal",
        states={"draft": [("readonly", False)]},
        readonly=True,
        required=True,
        default=lambda self: self.env["account.journal"].search(
            [("type", "=", "general")], limit=1
        ),
    )
    date = fields.Date(
        "Date Account",
        states={"draft": [("readonly", False)]},
        readonly=True,
        help="Keep empty to use the period of the validation(Payslip) date.",
    )
    move_id = fields.Many2one(
        "account.move", "Accounting Entry", readonly=True, copy=False
    )

    def close_payslip_run(self):
        res = super(HrPayslipRun, self).close_payslip_run()
        list_moves = []
        if self.company_id.is_payroll_account_batch:
            for slip in self.slip_ids:
                date = slip.date or slip.date_to
                list_moves.append(slip.get_lines(slip, date, self.journal_id))

            list_account = []
            for move in list_moves:
                list_account += [item[2].get("account_id") for item in move]

            line_ids = []
            for account in list(set(list_account)):
                debit = 0
                credit = 0
                name = ""
                for move in list_moves:
                    for res in list(
                        filter(lambda x: x[2].get("account_id") == account, move)
                    ):
                        debit += res[2].get("debit")
                        credit += res[2].get("credit")
                        name = res[2].get("name")
                if account == self.journal_id.default_account_id.id:
                    diff = debit - credit
                    if diff > 0:
                        debit = diff
                        credit = 0
                    elif diff < 0:
                        credit = -diff
                        debit = 0
                    else:
                        credit = debit = 0
                if credit or debit:
                    line_ids.append(
                        (
                            0,
                            0,
                            {
                                "name": name,
                                "partner_id": False,
                                "account_id": account,
                                "journal_id": self.journal_id.id,
                                "date": date,
                                "debit": debit,
                                "credit": credit,
                            },
                        )
                    )

            move_dict = {
                "narration": self.name,
                "ref": self.name,
                "journal_id": self.journal_id.id,
                "date": self.date or self.date_end,
                "line_ids": line_ids,
            }
            move = self.env["account.move"].create(move_dict)
            self.write({"move_id": move.id, "date": self.date or self.date_end})
            move.post()
        return res

    def draft_payslip_run(self):
        if self.company_id.is_payroll_account_batch:
            moves = self.mapped("move_id")
            moves.filtered(lambda x: x.state == "posted").button_cancel()
            moves.unlink()
        return super(HrPayslipRun, self).draft_payslip_run()
