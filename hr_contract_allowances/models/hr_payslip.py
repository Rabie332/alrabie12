from odoo import models

from .browsable_object import AllowanceLine


class Payslip(models.Model):
    _inherit = "hr.payslip"

    def _get_base_local_dict(self, payslip):
        res = super()._get_base_local_dict(payslip)
        allowances_dict = {
            line.rule_id.code: line
            for line in payslip.contract_id.allowances_ids
            if line.rule_id.code
        }
        res.update(
            {
                "allowances": AllowanceLine(
                    payslip.employee_id.id, allowances_dict, self.env
                )
            }
        )
        return res
