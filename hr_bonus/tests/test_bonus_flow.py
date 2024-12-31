from datetime import date

from odoo import fields
from odoo.tools import mute_logger

from odoo.addons.hr_bonus.tests.common import TestBonusBase


class TestBonusFlow(TestBonusBase):
    @mute_logger("odoo.addons.base.models.ir_model", "odoo.models")
    def test_hr_bonus_request_flow(self):
        # ----------------------------------------
        # Bonus Flow
        # ----------------------------------------
        # Confirm bonus
        self.bonus.sudo(self.user_bonus_manager_id).action_confirm()

        # validate bonus
        self.bonus.sudo(self.user_bonus_manager_id).action_payed()

        # Test total amount for bonus by amount
        self.assertEqual(
            self.bonus.total_amount,
            self.bonus.amount * len(self.bonus.employee_ids),
            "Total amount is not correct",
        )

        # Test total amount for bonus_by_department
        self.assertEqual(
            self.bonus_by_department.total_amount, 450, "Total amount is not correct"
        )

        # Test total amount for bonus_by_percentage
        self.assertEqual(
            self.bonus_by_percentage.total_amount, 555, "Total amount is not correct"
        )

        # ----------------------------------------
        # Payroll
        # ----------------------------------------

        # Create payslip with employee
        payroll = (
            self.env["hr.payslip"]
            .with_user(self.user_payroll_id)
            .create(
                {
                    "employee_id": self.employee_id,
                    "contract_id": self.employee.contract_id.id,
                    "date_from": date(
                        fields.date.today().year, fields.date.today().month, 1
                    ),
                    "date_to": self.current_month_last_date,
                }
            )
        )
        payroll.onchange_employee()

        # Test the appearance of bonus in payslip inputs
        test_bonus_aid = payroll.input_line_ids.filtered(
            lambda line: line.name == "Prime Aid"
            and line.code == "aid"
            and line.amount == 150
        )

        self.assertTrue(test_bonus_aid)
