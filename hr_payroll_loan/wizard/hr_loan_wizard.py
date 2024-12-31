from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HrLoanWizard(models.TransientModel):
    _name = "hr.loan.wizard"
    _description = "Hr Loan Wizard"

    @api.model
    def _get_domain_period(self):
        loan_id = self.env.context.get("default_loan_id", False)
        loan = self.env["hr.loan"].browse(loan_id)
        periods = []
        if loan:
            periods = (
                self.env["hr.period"]
                .search(
                    [
                        ("date_end", "<=", loan.date_to),
                        ("date_start", ">=", loan.date_from),
                        ("state", "=", "open"),
                    ]
                )
                .ids
            )
        return [("id", "in", periods)]

    date_from = fields.Date(string="Start date of Discount")
    installment_number_paid = fields.Integer(string="Installments number paid")
    loan_id = fields.Many2one("hr.loan", string="loan")
    action = fields.Selection(
        [("across", "Across"), ("early_payment", "Early Payment")],
        required=1,
        string="Action",
    )
    number_months_to_postpone = fields.Integer("Number of months to postpone")
    reason = fields.Text(string="Reason", required=1)
    period_id = fields.Many2one(
        "hr.period", string="postponement period", domain=_get_domain_period
    )

    # ------------------------------------------------------------
    # Functions
    # ------------------------------------------------------------
    def schedule_payment(self):
        if self.action == "early_payment":
            date_from = self.date_from
        else:
            # date from is the date start of period
            if self.period_id:
                date_from = self.period_id.date_start + relativedelta(
                    months=self.number_months_to_postpone
                )
        installment_number_paid = self.installment_number_paid
        history = self.env["hr.loan.history"].create(
            {
                "loan_id": self.loan_id.id,
                "action": self.action,
                "date": fields.Date.today(),
                "reason": self.reason,
                "installment_number_paid": installment_number_paid,
                "number_months_to_postpone": self.number_months_to_postpone,
                "date_from": date_from,
            }
        )
        for loan_line in self.loan_id.loan_line_ids.filtered(
            lambda line: line.state == "unpaid"
        ):
            if self.action == "early_payment":
                # make line loan paid
                if installment_number_paid > 0:
                    loan_line.sudo().write(
                        {"date": fields.Date.today(), "state": "paid"}
                    )
                    installment_number_paid -= 1
                    date_to_discount = self.loan_id.date_to
                # recalculate dates of payment
                else:
                    if date_from:
                        date_start = self.loan_id.get_first_day(date_from, 0, 0)
                        date_stop = self.loan_id.get_last_day(date_from)
                        name = date_from.strftime("%m/%Y")
                        date_from = fields.Date.from_string(
                            str(date_from)
                        ) + relativedelta(months=1)
                        loan_line.sudo().write(
                            {
                                "date_start": date_start,
                                "date_stop": date_stop,
                                "name": name,
                            }
                        )

                        date_to_discount = date_stop

            else:
                # recalculate dates of payment
                history.period_id = self.period_id
                if date_from:
                    date_start = self.loan_id.get_first_day(date_from, 0, 0)
                    date_stop = self.loan_id.get_last_day(date_from)
                    name = date_from.strftime("%m/%Y")
                    date_from = fields.Date.from_string(str(date_from)) + relativedelta(
                        months=1
                    )
                    loan_line.sudo().write(
                        {"date_start": date_start, "date_stop": date_stop, "name": name}
                    )

                    date_to_discount = date_stop
        # change the date end of discount
        if date_to_discount:
            self.loan_id.date_to = date_to_discount

    # ------------------------------------------------------------
    # Constraints Method
    # ------------------------------------------------------------
    @api.constrains("number_months_to_postpone", "installment_number_paid")
    def _check_numbers(self):
        for wizard in self:
            if wizard.action == "across":
                loan_setting = wizard.env["hr.loan.setting"].search([], limit=1)
                if wizard.number_months_to_postpone == 0:
                    raise ValidationError(
                        _("Number of months to postpone must be greater than 0")
                    )
                elif (
                    wizard.number_months_to_postpone
                    and loan_setting.number_months_allowed_postpone
                    < wizard.number_months_to_postpone
                ):
                    raise ValidationError(
                        _("Number of months to postpone depassed %s")
                        % loan_setting.number_months_allowed_postpone
                    )
            else:
                if wizard.installment_number_paid == 0:
                    raise ValidationError(
                        _(
                            "Number of Installments number to paid must be greater than 0"
                        )
                    )
