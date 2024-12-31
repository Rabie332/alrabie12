from odoo import _, models


class HrPayslipRun(models.Model):
    _inherit = "hr.payslip.run"

    def print_xls_bank_report(self):
        """Print Payslip run report XlSX."""
        data = {"ids": [self.id], "form": self.read([])[0]}
        self.env.ref("farha_custom.payslip_run_bank_report_xlsx").report_file = _(
            "Payroll of month %s/%s submitted to the bank"
        ) % (self.date_end.month, self.date_end.year)
        return self.env.ref("farha_custom.payslip_run_bank_report_xlsx").report_action(
            self, data=data
        )


class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    def _get_employee_bonus(self, contracts, date_from, date_to):
        """Get input_line_bonus for employee."""
        if not contracts or not date_to or not date_from:
            return []
        employee_bonus = []
        period = self.env["hr.period"].find(date_from, date_to)
        contract = contracts[0]
        employee_id = contract.employee_id.id if contract.employee_id else False
        if employee_id and period:
            bonus = self.env["hr.bonus"].search(
                [
                    ("employee_ids", "in", [employee_id]),
                    ("hr_period_id", "<=", period.id),
                    ("hr_period_to_id", ">=", period.id),
                    ("state", "!=", "draft"),
                ]
            )
            for line in bonus:
                if line.bonus_method == "percentage" and line.compute_method == "wage":
                    amount = (contract.wage * line.percent) / 100.0
                else:
                    amount = line.amount
                inputs_val = {
                    "name": line.type_id.name,
                    "sequence": line.type_id.sequence,
                    "code": line.type_id.code,
                    "amount": amount,
                    "contract_id": contract.id,
                }
                employee_bonus.append(inputs_val)
        return employee_bonus
