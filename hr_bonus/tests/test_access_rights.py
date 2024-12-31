from odoo import tests
from odoo.exceptions import UserError
from odoo.tools import mute_logger

from odoo.addons.hr_bonus.tests.common import TestBonusBase


@tests.tagged("access_rights")
class TestBonusAccessRights(TestBonusBase):
    # ----------------------------------------
    # Confirm and validate
    # ----------------------------------------

    @mute_logger("odoo.models.unlink", "odoo.addons.mail.models.mail_mail")
    def test_bonus_confirm_by_user_employee(self):
        """User should not be able to confirm requests."""
        with self.assertRaises(UserError):
            self.bonus.with_user(self.user_employee_id).action_confirm()

    @mute_logger("odoo.models.unlink", "odoo.addons.mail.models.mail_mail")
    def test_bonus_confirm_by_hr_user(self):
        """User should be able to confirm requests."""
        self.bonus.with_user(self.user_hr_user_id).action_confirm()

    @mute_logger("odoo.models.unlink", "odoo.addons.mail.models.mail_mail")
    def test_bonus_validate_by_user_employee(self):
        """User should not be able to validate requests."""
        with self.assertRaises(UserError):
            self.bonus.with_user(self.user_employee_id).action_payed()

    @mute_logger("odoo.models.unlink", "odoo.addons.mail.models.mail_mail")
    def test_bonus_validate_by_hr_user(self):
        """User should not be able to validate requests."""
        with self.assertRaises(UserError):
            self.bonus.with_user(self.user_hr_user_id).action_payed()
