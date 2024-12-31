from odoo.tests import common

from odoo.addons.mail.tests.common import mail_new_test_user


class TestPurchaseRequestBase(common.TransactionCase):
    def setUp(self):
        super(TestPurchaseRequestBase, self).setUp()

        # Create user that has the group purchase_request_user

        self.user_purchase = mail_new_test_user(
            self.env,
            login="user_purchase",
            groups="purchase.group_purchase_user",
        )

        # link purchase_request_user to his employee

        self.employee_purchase_user = self.env["hr.employee"].create(
            {"name": "employee Purchase User", "user_id": self.user_purchase.id}
        )

        # Create user that has group group_purchase_manager and link it to his employee

        self.user_purchase_manager = mail_new_test_user(
            self.env,
            login="user_purchase_manager",
            groups="purchase.group_purchase_manager",
        )

        self.employee_purchase_manager = self.env["hr.employee"].create(
            {
                "name": "employee Purchase manager",
                "user_id": self.user_purchase_manager.id,
            }
        )

        # Create user that has group base.group_user and link it to his employee

        self.user = mail_new_test_user(self.env, login="user", groups="base.group_user")

        self.employee = self.env["hr.employee"].create(
            {
                "name": "Employee",
                "user_id": self.user.id,
                "parent_id": self.employee_purchase_user.id,
            }
        )
