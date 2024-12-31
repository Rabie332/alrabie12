# pylint: disable=invalid-name
from odoo.tests import common

from odoo.addons.mail.tests.common import mail_new_test_user


class OvertimeCommon(common.TransactionCase):
    def setUp(self):
        """SetUp."""
        super(OvertimeCommon, self).setUp()
        # Create user that has the group group_hr_evaluation_user and link it to his employee

        self.user_overtime_mandate = mail_new_test_user(
            self.env,
            login="user_overtime_mandate",
            groups="hr_overtime.group_hr_overtime_mandate_user",
        )

        self.overtime_hr_employee = self.env["hr.employee"].create(
            {
                "name": "employee overtime mandate",
                "user_id": self.user_overtime_mandate.id,
            }
        )

        # Create user that has group group_hr_overtime_mandate_manager
        # and link it to his employee

        self.user_manager = mail_new_test_user(
            self.env,
            login="user_manager",
            groups="hr_overtime.group_hr_overtime_mandate_user",
        )

        self.employee_manager = self.env["hr.employee"].create(
            {"name": "employee Hr", "user_id": self.user_manager.id}
        )
