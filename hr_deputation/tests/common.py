from odoo.tests import common

from odoo.addons.mail.tests.common import mail_new_test_user


class TestHrDeputationBase(common.TransactionCase):
    def setUp(self):
        super(TestHrDeputationBase, self).setUp()

        # Create user that has the group group_user and link it to his employee
        self.user = mail_new_test_user(self.env, login="user", groups="base.group_user")

        self.employee = self.env["hr.employee"].create(
            {
                "name": "Employee",
                "user_id": self.user.id,
                "job_id": self.env.ref("hr.job_consultant").id,
            }
        )

        # Create user that has the group group_hr_deputation_officer and link it to his employee
        self.user_officer = mail_new_test_user(
            self.env,
            login="user_officer",
            groups="hr_deputation.group_hr_deputation_user",
        )
        self.employee_officer = self.env["hr.employee"].create(
            {"name": "Officer deputation", "user_id": self.user_officer.id}
        )
        # Make employee_officer the manager of employee

        self.employee.write({"parent_id": self.employee_officer.id})

        # Create user that has the group group_hr_deputation_manager
        self.user_manager = mail_new_test_user(
            self.env,
            login="user_manager",
            groups="hr_deputation.group_hr_deputation_manager",
        )

        # Add deputation balance to employee

        self.deputation_stock = self.env["hr.employee.deputation.stock"].create(
            {"employee_id": self.employee.id, "deputation_available_stock": 30}
        )

        #  Get the request type from the demo

        self.deputation_type_mission = self.env.ref(
            "hr_deputation.request_type_hr_deputation_mission"
        )

        # Get the Riadh city from the demo

        self.riadh_city = self.env.ref("hr_deputation.res_city_hr_deputation_riadh")

        # Get stage send

        self.stage_send = self.env.ref("hr_deputation.hr_deputation_stage_send")

        # stage validate will be approved by user_public_holidays_manager

        self.stage_validate = self.env.ref("hr_deputation.hr_deputation_stage_validate")
        self.stage_validate.write(
            {"assign_type": "user", "default_user_id": self.user_manager}
        )
        # stage done will be send feedback to employee

        self.hr_deputation_stage_done = self.env.ref(
            "hr_deputation.hr_deputation_stage_done"
        )
        self.hr_deputation_stage_done.write(
            {"assign_type": "user", "default_user_id": self.employee.user_id}
        )
        # stage refuse will be send feedback to employee

        self.hr_deputation_stage_refused = self.env.ref(
            "hr_deputation.hr_deputation_stage_refused"
        )
        self.hr_deputation_stage_refused.write(
            {"assign_type": "user", "default_user_id": self.employee.user_id}
        )
