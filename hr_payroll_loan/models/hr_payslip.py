from odoo import _, fields, models


class HrPayslipInput(models.Model):
    _inherit = "hr.payslip.input"

    loan_line_ids = fields.Many2many(
        "hr.loan.line", "loan_line_input_rel", string="Loan Installments"
    )


class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    # ------------------------------------------------------------
    #  Methods
    # ------------------------------------------------------------
    def _get_employee_loans(self, contracts, date_from, date_to):
        """Get input_line_loans for employee."""
        if not contracts or not date_from or not date_to:
            return []
        employee_loans = []
        contract = contracts[0]
        employee_id = contract.employee_id.id
        if not employee_id:
            return []
        loans = self.env["hr.loan"].search(
            [("employee_id", "=", employee_id), ("state", "=", "done")]
        )
        loan_line_ids = loans.mapped("loan_line_ids")
        loan_line_ids = loan_line_ids.filtered(
            lambda loan_line: date_from <= loan_line.date_start <= date_to
            and not loan_line.state == "paid"
        )
        amount = sum(loan_line_ids.mapped("amount"))
        if amount:
            inputs_val = {
                "name": _("Loan"),
                "sequence": 6,
                "code": "LOAN",
                "amount": amount,
                "loan_line_ids": [(6, 0, loan_line_ids.ids)],
                "contract_id": contract.id,
            }
            employee_loans.append(inputs_val)
            return employee_loans

    # ------------------------------------------------------------
    # Business methods
    # ------------------------------------------------------------
    def get_inputs(self, contracts, date_from, date_to):
        """Add Employee Loans to inputs lines."""
        res = super(HrPayslip, self).get_inputs(contracts, date_from, date_to)
        employee_loans = self._get_employee_loans(contracts, date_from, date_to)
        if employee_loans:
            for line in employee_loans:
                res += [line]
        return res

    def action_payslip_done(self):

        """After confirm the payslip we must update the loan(date,state).

        - mark loan line as done
        - put current date in field date discount  :
        """
        date_start = fields.Date.from_string(self.date_from)
        date_stop = fields.Date.from_string(self.date_to)
        self.env["hr.loan"].update_loan(date_start, date_stop, self)
        return super(HrPayslip, self).action_payslip_done()
