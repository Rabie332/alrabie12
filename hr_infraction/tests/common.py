from odoo.tests import common

from odoo.addons.test_mail.tests.common import mail_new_test_user


class TestHrInfractionBase(common.TransactionCase):
    def setUp(self):
        super(TestHrInfractionBase, self).setUp()

        # Create user that has the group group_user and link it to his employee
        self.user = mail_new_test_user(self.env, login="user", groups="base.group_user")

        self.employee = self.env["hr.employee"].create(
            {"name": "Employee", "user_id": self.user.id}
        )

        # Create user that has the group hr_infraction_group_manager and link it to his employee
        self.user_infraction_manager = mail_new_test_user(
            self.env,
            login="user_manager",
            groups="hr_infraction.hr_infraction_group_manager",
        )
        self.employee_infraction_manager = self.env["hr.employee"].create(
            {"name": "Employee Infraction", "user_id": self.user_infraction_manager.id}
        )
