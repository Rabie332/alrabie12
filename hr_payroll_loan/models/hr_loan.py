from datetime import date, timedelta

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class HrLoan(models.Model):
    _name = "hr.loan"
    _inherit = "request"
    _description = "Loan"
    _order = "id desc"

    name = fields.Char(
        required=1, readonly=1, states={"draft": [("readonly", 0)]}, string="Name"
    )
    loan_line_ids = fields.One2many(
        "hr.loan.line", "loan_id", string="Installments", required=1, readonly=1
    )
    date_from = fields.Date(string="Start date of Discount", readonly=1)
    date_to = fields.Date(string="END date of Discount", readonly=1, index=1)
    amount = fields.Float(
        string="Loan Amount",
        required=1,
        readonly=0,
        states={"done": [("readonly", 1)], "cancel": [("readonly", 1)]},
    )
    installment_number = fields.Integer(string="Installments number", readonly=1)
    is_paid = fields.Boolean(compute="_compute_is_paid", string="Is Paid", store=True)
    loan_reason = fields.Text(
        "Loan Reason", required=1, readonly=1, states={"draft": [("readonly", 0)]}
    )
    active = fields.Boolean(default=True, string="Active")
    residual_amount = fields.Float(
        string="Residual Amount", compute="_compute_residual_amount", store=1
    )
    monthly_amount = fields.Float(
        string="Monthly Amount",
        required=1,
        readonly=0,
        states={"done": [("readonly", 1)], "cancel": [("readonly", 1)]},
    )
    any_amount = fields.Boolean(
        "Any Amount", readonly=1, states={"draft": [("readonly", 0)]}
    )
    attachments = fields.Many2many(
        "ir.attachment",
        string="Attachments",
        readonly=1,
        states={"draft": [("readonly", 0)], "in_progress": [("readonly", 0)]},
    )
    refuse_reason = fields.Text(string="Refuse Reason", readonly=1)
    history_early_payment_ids = fields.One2many(
        "hr.loan.history",
        "loan_id",
        domain=[("action", "=", "early_payment")],
        readonly=1,
        string="Early Payment Historys",
    )
    history_postpone_payment_ids = fields.One2many(
        "hr.loan.history",
        "loan_id",
        domain=[("action", "=", "across")],
        readonly=1,
        string="Postpone Payment Histories",
    )
    display_button_action = fields.Boolean(
        "Display Button Action", compute="_compute_display_button_action"
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
        readonly=1,
        states={"draft": [("readonly", 0)]},
    )
    display_button_set_to_draft = fields.Boolean(
        "Display set to draft button", compute="_compute_display_button"
    )
    # ------------------------------------------------------------
    # ORM methods
    # ------------------------------------------------------------


    @api.model
    def create(self, vals):
        record = super(HrLoan, self).create(vals)
        if record.attachments:
            record.attachments.write({'res_model': self._name, 'res_id': record.id})
        return record

    def write(self, vals):
        result = super(HrLoan, self).write(vals)
        if self.attachments:
            self.attachments.write({'res_model': self._name, 'res_id': self.id})
        return result
    
    
    def name_get(self):
        res = []
        for loan in self:
            res.append((loan.id, (loan.name)))
        return res

    def _sync_employee_details(self):
        for request in self:
            super(HrLoan, request)._sync_employee_details()
            if request.employee_id and request.employee_id.company_id:
                request.company_id = request.employee_id.company_id.id

    # ------------------------------------------------------------
    # Compute methods
    # ------------------------------------------------------------

    @api.depends("loan_line_ids.state")
    def _compute_residual_amount(self):
        for loan in self:
            paid_lines = loan.loan_line_ids.filtered(lambda line: line.state == "paid")
            amount_paid = sum(loan_line.amount for loan_line in paid_lines)
            loan.residual_amount = loan.amount - amount_paid

    @api.depends("loan_line_ids.state")
    def _compute_is_paid(self):
        for loan in self:
            loan.is_paid = False
            un_paid_lines = loan.loan_line_ids.filtered(
                lambda line: line.state == "unpaid"
            )
            if loan.loan_line_ids and not un_paid_lines:
                loan.is_paid = True

    @api.depends("stage_id")
    def _compute_display_button_action(self):
        for loan in self:
            loan.display_button_action = False
            if (
                loan.state == "done"
                and not loan.is_paid
                and loan.env.context.get("display_bottom", False)
            ):
                loan.display_button_action = True

    @api.depends("stage_id")
    def _compute_display_button(self):
        for rec in self:
            users = rec._get_approvers()
            rec.display_button_refuse = False
            rec.display_button_accept = False
            rec.display_button_send = False
            rec.display_button_set_to_draft = False
            if rec.state == "draft" and (
                (rec.create_uid and rec.create_uid.id == rec.env.uid)
                or rec.env.user.has_group("hr.group_hr_manager")
            ):
                rec.display_button_send = True
            elif rec.state == "in_progress" and (
                rec.env.uid in users or rec.env.user.has_group("hr.group_hr_manager")
            ):
                rec.display_button_accept = True
                rec.display_button_refuse = True
            # Display set to draft button
            users = rec._get_approvers()
            if rec.state == "in_progress" and (
                rec.env.user.id in users
                or rec.env.user.has_group("hr.group_hr_manager")
            ):
                rec.display_button_set_to_draft = True

    # ------------------------------------------------------------
    # Constraints methods
    # ------------------------------------------------------------
    def _check_employee(self):
        for loan in self:
            if loan.employee_id:
                # check of employee have unpaid loan
                unpaid_loan = loan.env["hr.loan"].search(
                    [
                        ("employee_id", "=", loan.employee_id.id),
                        ("state", "not in", ["cancel", "draft"]),
                        ("is_paid", "=", False),
                        ("id", "!=", loan.id),
                    ]
                )
                if unpaid_loan:
                    raise UserError(
                        _(
                            "You cannot apply for a loan because you have a loan not paid!"
                        )
                    )
                # check if employee have more than one year in work
                contract = (
                    loan.env["hr.contract"]
                    .sudo()
                    .search(
                        [
                            ("employee_id", "=", loan.employee_id.id),
                            ("state", "=", "open"),
                        ],
                        limit=1,
                    )
                )
                if contract.date_start:
                    today_date = fields.Date.from_string(fields.Date.today())
                    date_work = fields.Date.from_string(contract.date_start)
                    years = (today_date - date_work).days / 354
                    if 0 < years < 1:
                        raise UserError(
                            _(
                                "You cannot apply for a loan "
                                "because you have not spent a year working!"
                            )
                        )
                # check if employee have more than one year after paid last loan
                date_to = loan.search(
                    [
                        ("employee_id", "=", loan.employee_id.id),
                        ("id", "!=", loan.id),
                        ("state", "=", "done"),
                    ],
                    order="date_to desc",
                    limit=1,
                ).date_to
                if date_to:
                    today_date = fields.Date.from_string(fields.Date.today())
                    date_to = fields.Date.from_string(date_to)
                    years = (today_date - date_to).days / 354
                    if 0 < years < 1:
                        raise UserError(
                            _(
                                "You cannot apply for a loan because"
                                " you have not spent a year after last loan!"
                            )
                        )

    @api.constrains("monthly_amount", "amount", "any_amount")
    def _check_amounts(self):
        for loan in self:
            if loan.employee_id:
                loan_setting = loan.env["hr.loan.setting"].search([], limit=1)
                basic_salary = (
                    loan.env["hr.contract"]
                    .sudo()
                    .search(
                        [
                            ("employee_id", "=", loan.employee_id.id),
                            ("state", "=", "open"),
                        ],
                        limit=1,
                    )
                    .wage
                )
                # check if loan amount depassed the loan amount in loan setting
                if (
                    loan.amount
                    and basic_salary * loan_setting.loan_amount < loan.amount
                ):
                    raise UserError(
                        _("Monthly Amount depassed your salary %s")
                        % loan_setting.loan_amount
                    )
                # check if monthly amount depassed the employee basic salary
                if loan.monthly_amount and basic_salary < loan.monthly_amount:

                    raise UserError(
                        _("Monthly amount depassed your salary %s") % basic_salary
                    )
                # check if monthly amount depassed the percent monthly installment salary
                if not loan.any_amount:
                    if (
                        loan_setting
                        and loan.monthly_amount
                        > (basic_salary / 100)
                        * loan_setting.percent_monthly_installment_salary
                    ):
                        raise UserError(
                            _("Installment amount cannot be greater than %s")
                            % (
                                (basic_salary / 100)
                                * loan_setting.percent_monthly_installment_salary
                            )
                        )

    @api.constrains("installment_number")
    def _check_installment_number(self):
        for loan in self:
            # check if installment number depassed the installment number indicated in setting
            loan_setting = loan.env["hr.loan.setting"].search([], limit=1)
            if (
                loan_setting
                and loan.installment_number
                and loan.installment_number > loan_setting.installment_number
            ):
                raise UserError(
                    _("Installment Number depassed %s")
                    % (loan_setting.installment_number)
                )

    @api.constrains("monthly_amount")
    def _check_monthly_amount(self):
        """check mouthly amount"""
        for loan in self:
            if loan.monthly_amount <= 0:
                raise ValidationError(_("Monthly amount must be greater than 0."))

    # ------------------------------------------------------------
    # Onchange methods
    # ------------------------------------------------------------

    @api.onchange("amount", "monthly_amount", "date_from")
    def _onchange_date(self):
        if self.amount and self.monthly_amount:
            self.generate_lines(self.amount, self.monthly_amount)

    # ------------------------------------------------------------
    # Business methods
    # ------------------------------------------------------------

    def get_first_day(self, date_auth, d_years=0, d_months=0):
        """To take the first day of date."""
        year, month = date_auth.year + d_years, date_auth.month + d_months
        adiv, month = divmod(month - 1, 12)
        return date(year + adiv, month + 1, 1)

    def get_last_day(self, date_auth):
        """To take the last day of date."""
        date_res = self.get_first_day(date_auth, 0, 1) + timedelta(-1)
        return date_res

    def update_lines(self):
        """Update dates of lines."""
        date_from = self.date_from
        date_stop = False
        for line in self.loan_line_ids:
            line.date_start = self.get_first_day(date_from, 0, 0)
            line.date_stop = self.get_last_day(date_from)
            date_stop = line.date_stop
            line.name = date_from.strftime("%m/%Y")
            date_from = fields.Date.from_string(str(date_from)) + relativedelta(
                months=1
            )
        self.date_to = date_stop

    def generate_lines(self, loan_amount, monthly_amount):
        """Generate installments.

        :param loan_amount:
        :param monthly_amount:
        :param date_from:
        :return:
        """
        # get lines
        amount = 0.0
        diff = loan_amount - amount
        installment_number = 0
        final_amount = monthly_amount
        date_start = False
        date_stop = False
        name = ""
        date_from = self.date_from
        self.loan_line_ids = [(6, 0, [])]
        while diff > 0:
            if date_from:
                date_start = self.get_first_day(date_from, 0, 0)
                date_stop = self.get_last_day(date_from)
                name = date_from.strftime("%m/%Y")
                date_from = fields.Date.from_string(str(date_from)) + relativedelta(
                    months=1
                )
            created_line = self.env["hr.loan.line"].new(
                {
                    "loan_id": self.id,
                    "amount": final_amount,
                    "date_start": date_start,
                    "date_stop": date_stop,
                    "name": name,
                }
            )
            if created_line not in self.loan_line_ids:
                self.loan_line_ids += created_line
            installment_number += 1
            amount += monthly_amount
            diff = loan_amount - amount
            if diff >= monthly_amount:
                final_amount = monthly_amount
            else:
                final_amount = diff
        self.installment_number = installment_number

    def action_accept(self):
        for loan in self:
            super(HrLoan, loan).action_accept()
            if loan.stage_id.state == "done":
                date = fields.Date.from_string(fields.Date.today()) + relativedelta(
                    months=1
                )
                loan.date_from = loan.get_first_day(date, 0, 0)
                loan.update_lines()

    def action_send(self):
        """Send the request to be approved by the right users."""
        for loan in self:
            loan._check_employee()
            super(HrLoan, loan).action_send()

    def update_loan(self, date_from, date_to, payslip):
        """After confirm payslip we must update the loan.

        - mark loan line as done
        - put current date in field date : date of discount
        """
        # search all loan for this employee
        loans = self.search(
            [
                ("employee_id", "=", payslip.employee_id.id),
                ("state", "=", "done"),
                ("is_paid", "=", False),
            ]
        )
        lines = []
        for loan in loans:
            lines += loan.env["hr.loan.line"].search(
                [
                    ("date_start", "=", date_from),
                    ("date_stop", "=", date_to),
                    ("state", "=", "unpaid"),
                    ("loan_id", "=", loan.id),
                ]
            )
        for line in lines:
            line.write(
                {"date": fields.Date.today(), "state": "paid", "payslip_id": payslip.id}
            )
        return lines

    def toggle_active(self):
        for loan in self:
            loan.with_context(active_test=False).loan_line_ids.filtered(
                lambda line: line.active == loan.active
            ).toggle_active()
        super(HrLoan, self).toggle_active()

    def set_to_draft(self):
        """Set to draft."""
        for request in self:
            request.stage_id = request._get_next_stage(stage_type="default")
            request._onchange_stage_id()
            request.activity_schedule(
                "hr_payroll_loan.mail_hr_loan_set_to_draft",
                user_id=request.create_uid.id,
            )

    def get_approvals_details(self):
        new_values = {}
        values = super(HrLoan, self).get_approvals_details()
        for key, value in values.items():
            if key not in ["مسودة", "Draft"]:
                new_values.update({key: value})
        return new_values

    def get_approvals(self):
        """Return stage name and approver and his signature."""
        for request in self:
            stages = request.sudo().get_approvals_details()
            approved_stages = []
            for stage in stages:
                approver = stages[stage]["approver"]
                stage_obj = request.env["request.stage"].browse(
                    stages[stage]["stage_id"]
                )

                if stage_obj and stage_obj.appears_in_loan_report:
                    vals = {
                        "stage": stage,
                        "approver_name": approver.name,
                        "signature": False,
                        "sequence": stage_obj.sequence,
                        "date": stages[stage]["date"].strftime("%Y-%m-%d")
                        if stages[stage]["date"]
                        else "",
                    }
                    if approver:
                        vals["signature"] = approver.digital_signature
                    approved_stages.append(vals)
            return sorted(approved_stages, key=lambda i: i["sequence"])


class HrLoanLine(models.Model):
    _name = "hr.loan.line"
    _description = "Loan Line"

    loan_id = fields.Many2one("hr.loan", string="Loan", ondelete="cascade", index=1)
    amount = fields.Float(string="Installment Amount", required=1)
    date = fields.Date(string="Date of discount", required=False, index=1)
    date_start = fields.Date(string="Start Period", required=False, index=1)
    date_stop = fields.Date(string="End Period", required=False, index=1)
    state = fields.Selection(
        [("unpaid", "Unpaid"), ("paid", "Paid")],
        string="State",
        readonly=1,
        index=1,
        default="unpaid",
    )
    name = fields.Char(string="Period")
    payslip_id = fields.Many2one("hr.payslip", string="Payslip")
    active = fields.Boolean(default=True, string="Active")


class HrLoanHistory(models.Model):
    _name = "hr.loan.history"
    _description = "Loan History"

    loan_id = fields.Many2one("hr.loan", string="Loan", ondelete="cascade")
    action = fields.Selection(
        [("across", "Across"), ("early_payment", "Early Payment")], string="Action"
    )
    reason = fields.Text(string="Reason")
    date = fields.Date(string="Date of Action")
    date_from = fields.Date(string="Start date of Discount")
    period_id = fields.Many2one("hr.period", string="postponement period")
    installment_number_paid = fields.Integer(string="Installments number paid")
    number_months_to_postpone = fields.Integer("Number of months to postpone")
