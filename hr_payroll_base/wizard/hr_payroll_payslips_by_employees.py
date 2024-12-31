from odoo import models


class HrPayslipEmployees(models.TransientModel):
    _inherit = "hr.payslip.employees"

    def _get_available_contracts_domain(self):
        domain = [
            ("contract_ids.state", "in", ("open", "close")),
        ]
        context = self.env.context or {}
        if (
            context
            and context.get("active_id", False)
            and context.get("active_model", False)
        ):
            model_obj = self.env[context.get("active_model")]
            payslip_run = model_obj.browse(context.get("active_id"))
            # get employees of company of the payslip run
            domain += [("company_id", "=", payslip_run.company_id.id)]
            # get employees that have categories of payslip run
            if payslip_run and payslip_run.category_ids:
                domain += [("category_ids", "in", payslip_run.category_ids.ids)]
        return domain
