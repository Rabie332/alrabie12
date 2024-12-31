from odoo import _, fields, models


class HrLoanSetting(models.Model):
    _name = "hr.loan.setting"
    _description = "Loan Setting"

    name = fields.Char(string="Name")
    installment_number = fields.Integer(string="Installments number")
    percent_monthly_installment_salary = fields.Integer(
        string="Percentage installment monthly of the total salary"
    )
    loan_amount = fields.Float(string="Loan Amount")
    number_months_allowed_postpone = fields.Integer(
        "Number of months allowed to be deferred"
    )
    # ------------------------------------------------------------
    # Business methods
    # ------------------------------------------------------------

    def button_setting(self):
        """Show view form for loan main settings.

        :return: Dictionary contain view form of hr.loan.setting
        """
        loan_setting = self.env["hr.loan.setting"].search([], limit=1)
        if loan_setting:
            return {
                "name": _("Loan Setting"),
                "view_type": "form",
                "view_mode": "form",
                "res_model": "hr.loan.setting",
                "view_id": False,
                "type": "ir.actions.act_window",
                "res_id": loan_setting.id,
            }
