from odoo import models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def _get_employee_info(self, contract):
        """Get basic salary, gross salary and net salary for employee."""
        basic_salary = gross_salary = net_salary = 0.0
        if contract:
            basic_salary = net_salary = gross_salary = contract.wage
            # get the last payslip of employee
            last_payslip = self.env["hr.payslip"].search(
                [
                    ("employee_id", "=", self.id),
                    ("contract_id", "=", contract.id),
                    ("state", "=", "done"),
                ],
                order="hr_period_id desc",
                limit=1,
            )
            if last_payslip:
                line_net = last_payslip.line_ids.filtered(
                    lambda line: line.code == "NET"
                )
                if line_net:
                    net_salary = line_net[0].total
                line_gross = last_payslip.line_ids.filtered(
                    lambda line: line.code == "GROSS"
                )
                if line_gross:
                    gross_salary = line_gross[0].total
        return basic_salary, gross_salary, net_salary
