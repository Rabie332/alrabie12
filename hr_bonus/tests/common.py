from datetime import date

from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.tests import common

from odoo.addons.mail.tests.common import mail_new_test_user


class TestBonusBase(common.TransactionCase):
    def setUp(self):
        super(TestBonusBase, self).setUp()

        # Test users to use through the various tests
        self.user_bonus_manager = mail_new_test_user(
            self.env, login="sebastien", groups="hr_bonus.hr_bonus_group_manager"
        )
        self.user_bonus_manager_id = self.user_bonus_manager.id

        self.user_hr_user = mail_new_test_user(
            self.env, login="bastien", groups="hr.group_hr_user"
        )
        self.user_hr_user_id = self.user_hr_user.id

        self.user_employee = mail_new_test_user(
            self.env, login="george", groups="base.group_user"
        )
        self.user_employee_id = self.user_employee.id

        self.user_payroll = mail_new_test_user(
            self.env, login="fabien", groups="hr_payroll.group_hr_payroll_manager"
        )
        self.user_payroll_id = self.user_payroll.id
        # Hr Data

        Department = self.env["hr.department"].with_context(tracking_disable=True)

        self.hr_dept = Department.create({"name": "Human Resources"})
        self.employee_bonus_manager = self.env["hr.employee"].create(
            {
                "name": "Sebastien Bonus manager",
                "user_id": self.user_bonus_manager_id,
                "department_id": self.hr_dept.id,
            }
        )
        self.employee_bonus_manager_id = self.employee_bonus_manager.id

        self.employee_hr_user = self.env["hr.employee"].create(
            {
                "name": "bastien Employee",
                "user_id": self.user_hr_user_id,
                "department_id": self.hr_dept.id,
            }
        )

        self.employee_hr_user_id = self.employee_hr_user.id

        self.employee = self.env["hr.employee"].create(
            {
                "name": "George Employee",
                "user_id": self.user_employee_id,
                "department_id": self.hr_dept.id,
            }
        )

        self.employee_id = self.employee.id

        current_year_first_date = date(fields.date.today().year, 1, 1)
        current_year_last_date = date(fields.date.today().year, 12, 31)

        contract = self.env["hr.contract"].create(
            {
                "name": "Test",
                "wage": 1000,
                "wage_net": 1000,
                "employee_id": self.employee.id,
                "state": "open",
                "date_start": current_year_first_date,
                "date_end": current_year_last_date,
                "struct_id": self.env.ref("hr_payroll.structure_base").id,
            }
        )

        contract_for_hr = self.env["hr.contract"].create(
            {
                "name": "Test hr",
                "wage": 1500,
                "wage_net": 1500,
                "employee_id": self.employee_hr_user.id,
                "state": "open",
                "date_start": current_year_first_date,
                "date_end": current_year_last_date,
                "struct_id": self.env.ref("hr_payroll.structure_base").id,
            }
        )

        contract_for_bonus_manager = self.env["hr.contract"].create(
            {
                "name": "Test bonus manger",
                "wage": 1200,
                "wage_net": 1200,
                "employee_id": self.employee_bonus_manager.id,
                "state": "open",
                "date_start": current_year_first_date,
                "date_end": current_year_last_date,
                "struct_id": self.env.ref("hr_payroll.structure_base").id,
            }
        )

        self.employee.write({"contract_id": contract.id})
        self.employee_hr_user.write({"contract_id": contract_for_hr.id})
        self.employee_bonus_manager.write(
            {"contract_id": contract_for_bonus_manager.id}
        )

        bonus_manager_group = self.env.ref("hr_bonus.hr_bonus_group_manager")
        bonus_manager_group.write({"users": [(4, self.user_payroll_id)]})

        self.employee_payroll = self.env["hr.employee"].create(
            {"name": "Fabien Payroll", "user_id": self.user_payroll_id}
        )

        self.employee_payroll_id = self.employee_payroll.id

        # Create common bonus flow variables
        self.structure_id = self.env.ref("hr_payroll.structure_base")
        self.category_id = self.env.ref("hr_payroll.O_ALW").id
        self.bonus_type = self.env["hr.salary.rule"].create(
            {
                "name": "Prime Aid",
                "code": "aid",
                "sequence": "23",
                "is_bonus": True,
                "category_id": self.category_id,
                "structure_ids": [(6, 0, [self.structure_id.id])],
            }
        )
        self.bonus_type.onchange_bonus()
        self.bonus_type.onchange_code()

        self.fiscale_year = self.env["hr.fiscalyear"].create(
            {
                "name": "Year " + str(fields.date.today().year),
                "schedule_pay": "monthly",
                "date_start": current_year_first_date,
                "date_end": current_year_last_date,
            }
        )

        self.current_month_last_date = (
            date(fields.date.today().year, fields.date.today().month, 1)
            + relativedelta(months=1)
            - relativedelta(days=1)
        )

        self.current_period = self.env["hr.period"].find(
            date(fields.date.today().year, fields.date.today().month, 1),
            self.current_month_last_date,
        )
        if not self.current_period:
            # create fiscal year periods
            self.fiscale_year.create_periods()

            # Get current period
            self.current_period = self.fiscale_year.period_ids[
                fields.date.today().month - 1
            ]
        self.current_period.number_worked_days = 22
        #  Create bonus with the current period
        self.bonus = (
            self.env["hr.bonus"]
            .with_user(self.user_bonus_manager_id)
            .create(
                {
                    "date": fields.date.today(),
                    "bonus_method": "amount",
                    "target": "employee",
                    "employee_ids": [
                        (
                            6,
                            0,
                            [
                                self.employee_bonus_manager_id,
                                self.employee_hr_user_id,
                                self.employee_id,
                            ],
                        )
                    ],
                    "amount": 150,
                    "type_id": self.bonus_type.id,
                    "hr_period_id": self.current_period.id,
                }
            )
        )
        self.bonus.compute_gross_per_employee()

        #     Create a bonus by departement with the period is the current month
        self.bonus_by_department = (
            self.env["hr.bonus"]
            .with_user(self.user_bonus_manager_id)
            .create(
                {
                    "date": fields.date.today(),
                    "bonus_method": "amount",
                    "target": "department",
                    "department_ids": [(6, 0, [self.hr_dept.id])],
                    "amount": 150,
                    "type_id": self.bonus_type.id,
                    "hr_period_id": self.current_period.id,
                }
            )
        )
        self.bonus_by_department.onchange_department_ids()
        self.bonus_by_department.compute_gross_per_employee()

        # Add 'contract_manager security group' to bonus manager to check contracts wages.
        contract_manager_group = self.env.ref("hr_contract.group_hr_contract_manager")
        contract_manager_group.write({"users": [(4, self.user_bonus_manager_id)]})
        self.bonus_by_percentage = (
            self.env["hr.bonus"]
            .with_user(self.user_bonus_manager_id)
            .create(
                {
                    "date": fields.date.today(),
                    "bonus_method": "percentage",
                    "target": "employee",
                    "employee_ids": [
                        (
                            6,
                            0,
                            [
                                self.employee_bonus_manager_id,
                                self.employee_hr_user_id,
                                self.employee_id,
                            ],
                        )
                    ],
                    "amount": 15,
                    "type_id": self.bonus_type.id,
                    "hr_period_id": self.current_period.id,
                }
            )
        )
