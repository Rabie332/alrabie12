from datetime import date

from odoo.exceptions import UserError
from odoo.tests import Form
from odoo.tools import mute_logger, relativedelta

from .common import TestHrDeputationBase


class TestHrDeputationExtentionFlow(TestHrDeputationBase):
    @mute_logger("odoo.addons.base.models.ir_model", "odoo.models")
    def test_hr_deputation_extension_request_flow(self):
        # ----------------------------------------
        # Extend a deputation request that is in the future
        # ----------------------------------------

        # Create deputation

        deputation_object = self.env["hr.deputation"].with_user(self.user)
        deputation_form = Form(deputation_object)
        deputation_form.employee_id = self.employee
        deputation_form.request_type_id = self.deputation_type_mission
        deputation_form.date_from = date.today() + relativedelta(days=-2)
        deputation_form.date_to = date.today() + relativedelta(days=+2)
        deputation_form.task_name = "Work mission"
        deputation_form.city_id = self.riadh_city
        deputation_form.stage_id = self.stage_send
        deputation_form.read_reviewed_policies_regulations = True
        self.deputation = deputation_form.save()

        # check request has the right stage and state

        self.assertEqual(self.deputation.stage_id.name, "Send")
        self.assertEqual(self.deputation.state, "draft")

        # user sends his request.

        self.deputation.with_user(self.user).action_send()

        #  Manager accepts the request

        self.deputation.with_user(self.user_manager).action_accept()

        # stage validate will be approved by user_manager

        self.send_extension = self.env.ref(
            "hr_deputation.hr_deputation_extension_stage_send"
        )
        self.validate_extension = self.env.ref(
            "hr_deputation.hr_deputation_extension_stage_validate"
        )
        self.validate_extension.write(
            {"assign_type": "user", "default_user_id": self.user_manager}
        )
        # Create extension request and refuse it by deputation manager

        extension_vals = {}
        context = self.deputation.button_extend()["context"]
        extension_vals["employee_id"] = context["default_employee_id"]
        extension_vals["date_from"] = context["default_date_from"]
        extension_vals["date_to"] = context["default_date_to"]
        extension_vals["duration"] = context["default_duration"]
        extension_vals["deputation_id"] = context["default_deputation_id"]
        extension_vals["new_duration"] = 3
        extension_vals["reason"] = "Extension reason"
        extension_vals["stage_id"] = self.send_extension.id
        self.extension_deputation = (
            self.env["hr.deputation.extension"]
            .with_user(self.user)
            .create(extension_vals.copy())
        )

        # test constraint _check_constraints: Please check the extension time.
        with self.assertRaises(UserError):
            self.extension_deputation.write({"new_duration": -5})

        # user sends his request.

        self.extension_deputation.with_user(self.user).action_send()

        # check user and user_manager are followers of this request

        self.assertIn(
            self.user_manager.partner_id,
            self.extension_deputation.message_partner_ids,
            "Deputation manager is not added as an extension request followers.",
        )
        self.assertIn(
            self.user.partner_id,
            self.extension_deputation.message_partner_ids,
            "User is not added as an extension request followers.",
        )

        # check the next activity is correct (activity's name and its assigned to right user)

        self.assertEqual(
            self.extension_deputation.activity_type_id.name,
            "Deputation Extension is ready to be approved",
        )
        self.assertEqual(
            self.extension_deputation.activity_ids[0].user_id,
            self.user_manager,
            "Activity should be assigned to Deputation manager.",
        )

        # check the request has the right stage and state

        self.assertEqual(self.extension_deputation.stage_id.name, "Validate")
        self.assertEqual(self.extension_deputation.state, "in_progress")

        # Refuse request by officer

        self.extension_deputation.with_user(self.user_manager).action_refuse()

        # check request has the right stage and state

        self.assertEqual(self.extension_deputation.stage_id.name, "Refused")
        self.assertEqual(self.extension_deputation.state, "cancel")

        # User should receive an email notification of refused request
        partners = []
        notified_partner_ids = [
            message.notified_partner_ids.ids
            for message in self.extension_deputation.message_ids
            if message.notified_partner_ids
        ]
        for partner in notified_partner_ids:
            for partner_id in partner:
                partners.append(partner_id)
        # todo
        # self.assertIn(self.user.partner_id.id, partners)

        # Create extension request and accept it by officer

        self.other_extension_deputation = (
            self.env["hr.deputation.extension"]
            .with_user(self.user)
            .create(extension_vals.copy())
        )

        # user sends his request.

        self.other_extension_deputation.with_user(self.user).action_send()

        # accept request by user_officer

        self.other_extension_deputation.with_user(self.user_officer).action_accept()

        # check the name of stage and state.

        self.assertEqual(self.other_extension_deputation.stage_id.name, "Done")
        self.assertEqual(self.other_extension_deputation.state, "done")

        # employee should receive an email notification of approved request
        partners = []
        notified_partner_ids = [
            message.notified_partner_ids.ids
            for message in self.other_extension_deputation.message_ids
            if message.notified_partner_ids
        ]
        for partner in notified_partner_ids:
            for partner_id in partner:
                partners.append(partner_id)
        # todo
        # self.assertIn(self.user.partner_id.id, partners)
