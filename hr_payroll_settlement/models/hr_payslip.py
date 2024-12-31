from odoo import _, models


class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    # --------------------------------------------------------------------
    # Business methods
    # --------------------------------------------------------------------
    def _get_employee_settlement(self, contracts, date_from, date_to):
        """Get input_line_settlement for employee."""
        if not contracts or not date_to or not date_from:
            return []
        employee_settlement = []
        period = self.env["hr.period"].find(date_from, date_to)
        contract = contracts[0]
        employee_id = contract.employee_id.id if contract.employee_id else False
        if employee_id and period:
            settlements = (
                self.env["hr.settlement"]
                .sudo()
                .search(
                    [
                        ("employee_id", "=", employee_id),
                        ("period_id", "=", period.id),
                        ("state", "=", "done"),
                    ]
                )
            )
            # get addition settlement
            addition_amount = sum(
                line.amount
                for line in settlements.filtered(lambda line: line.type == "addition")
            )
            if addition_amount:
                inputs_val = {
                    "name": _("Addition Settlement"),
                    "code": "ADD",
                    "amount": addition_amount,
                    "contract_id": contract.id,
                }
                employee_settlement.append(inputs_val)
            # get deduction settlement
            deduction_amount = sum(
                line.amount
                for line in settlements.filtered(lambda line: line.type == "deduction")
            )
            if deduction_amount:
                inputs_val = {
                    "name": _("Deduction Settlement"),
                    "code": "DED",
                    "amount": deduction_amount,
                    "contract_id": contract.id,
                }
                employee_settlement.append(inputs_val)
        return employee_settlement

    def get_inputs(self, contracts, date_from, date_to):
        """Add Employee settlement to inputs lines."""
        res = super(HrPayslip, self).get_inputs(contracts, date_from, date_to)
        employee_settlement = self._get_employee_settlement(
            contracts, date_from, date_to
        )
        for line in employee_settlement:
            res += [line]
        return res
