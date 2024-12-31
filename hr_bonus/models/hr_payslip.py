from odoo import fields, models


class HrPayslipInput(models.Model):
    _inherit = "hr.payslip.input"

    bonus_id = fields.Many2one(
        "hr.bonus",
        string="Bonus",
        ondelete="cascade",
    )


class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    def get_inputs(self, contracts, date_from, date_to):
        """Add Employee bonus to inputs lines."""
        res = super(HrPayslip, self).get_inputs(contracts, date_from, date_to)
        employee_bonus = self._get_employee_bonus(contracts, date_from, date_to)
        for line in employee_bonus:
            res += [line]
        return res

    def _get_employee_bonus(self, contracts, date_from, date_to):
        """Get input_line_bonus for employee."""
        if not contracts or not date_to or not date_from:
            return []
        employee_bonus = []
        contract = contracts[0]
        employee_id = contract.employee_id.id if contract.employee_id else False
        if employee_id and self.hr_period_id:
            domain = [
                ("employee_ids", "in", [employee_id]),
                ("hr_period_id", "=", self.hr_period_id.id),
                ("state", "!=", "draft"),
            ]
            if self.is_specific_struct:
                domain.append(("type_id.is_specific_bonus", "=", True))
            else:
                domain.append(("type_id.is_specific_bonus", "=", False))
            hr_bonus = self.env["hr.bonus"].search(domain)
            for bonus in hr_bonus:
                if bonus.bonus_method == "percentage":
                    amount = (contract.wage * bonus.amount) / 100.0
                else:
                    if bonus.line_ids:
                        amount = bonus.line_ids.filtered(
                            lambda l: l.employee_id.id == employee_id
                        ).amount
                    else:
                        amount = bonus.amount
                inputs_val = {
                    "name": bonus.type_id.name,
                    "sequence": bonus.type_id.sequence,
                    "code": bonus.type_id.code,
                    "amount": amount,
                    "contract_id": contract.id,
                    "bonus_id": bonus.id,
                }
                employee_bonus.append(inputs_val)
        return employee_bonus
