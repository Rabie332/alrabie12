from datetime import date

from odoo.tests import Form
from odoo.tools import mute_logger, relativedelta

from .common import TestHrDeputationBase


class TestHrDeputationFlow(TestHrDeputationBase):
    @mute_logger("odoo.addons.base.models.ir_model", "odoo.models")
    def test_hr_deputation_request_flow(self):
        # ----------------------------------------
        # Cancel a deputation request that is in the future
        # ----------------------------------------

        # Create deputation

        deputation_object = self.env["hr.deputation"].with_user(self.user)
        deputation_form = Form(deputation_object)
        deputation_form.employee_id = self.employee
        deputation_form.request_type_id = self.deputation_type_mission
        deputation_form.date_from = date.today() + relativedelta(days=+9)
        deputation_form.date_to = date.today() + relativedelta(days=+10)
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

        self.send_cancellation = self.env.ref(
            "hr_deputation.hr_deputation_cancel_stage_send"
        )
        self.validate_cancellation = self.env.ref(
            "hr_deputation.hr_deputation_cancel_stage_validate"
        )
        self.validate_cancellation.write(
            {"assign_type": "user", "default_user_id": self.user_manager}
        )

        # Create cancellation request and refuse it by deputation manager

        cancellation_vals = {}
        context = self.deputation.button_cancel()["context"]
        cancellation_vals["employee_id"] = context["default_employee_id"]
        cancellation_vals["date_from"] = context["default_date_from"]
        cancellation_vals["date_to"] = context["default_date_to"]
        cancellation_vals["duration"] = context["default_duration"]
        cancellation_vals["deputation_id"] = context["default_deputation_id"]
        cancellation_vals["reason"] = "Cancellation reason"
        cancellation_vals["stage_id"] = self.send_cancellation.id
        self.cancel_deputation = (
            self.env["hr.deputation.cancellation"]
            .with_user(self.user)
            .create(cancellation_vals.copy())
        )

        # user sends his request.

        self.cancel_deputation.with_user(self.user).action_send()

        # check user and user_manager are followers of this request

        self.assertIn(
            self.user_manager.partner_id,
            self.cancel_deputation.message_partner_ids,
            "Deputation manager is not added as a cancel request followers.",
        )
        self.assertIn(
            self.user.partner_id,
            self.cancel_deputation.message_partner_ids,
            "User is not added as a cancel request followers.",
        )

        # check the next activity is correct (activity's name and its assigned to right user)

        self.assertEqual(
            self.cancel_deputation.activity_type_id.name,
            "Deputation Cancellation is ready to be approved",
        )
        self.assertEqual(
            self.cancel_deputation.activity_ids[0].user_id,
            self.user_manager,
            "Activity should be assigned to Deputation manager.",
        )

        # check the request has the right stage and state

        self.assertEqual(self.cancel_deputation.stage_id.name, "Validate")
        self.assertEqual(self.cancel_deputation.state, "in_progress")

        # Refuse request by officer

        self.cancel_deputation.with_user(self.user_manager).action_refuse()

        # check request has the right stage and state

        self.assertEqual(self.cancel_deputation.stage_id.name, "Refused")
        self.assertEqual(self.cancel_deputation.state, "cancel")

        # User should receive an email notification of refused request
        partners = []
        notified_partner_ids = [
            message.notified_partner_ids.ids
            for message in self.cancel_deputation.message_ids
            if message.notified_partner_ids
        ]
        for partner in notified_partner_ids:
            for partner_id in partner:
                partners.append(partner_id)
        # todo
        # self.assertIn(self.user.partner_id.id, partners)

        # Create cancellation request and accept it by officer

        self.other_cancel_deputation = (
            self.env["hr.deputation.cancellation"]
            .with_user(self.user)
            .create(cancellation_vals.copy())
        )

        # user sends his request.

        self.other_cancel_deputation.with_user(self.user).action_send()

        # accept request by user_officer

        self.other_cancel_deputation.with_user(self.user_officer).action_accept()

        # check the name of stage and state.

        self.assertEqual(self.other_cancel_deputation.stage_id.name, "Done")
        self.assertEqual(self.other_cancel_deputation.state, "done")

        # employee should receive an email notification of approved request
        partners = []
        notified_partner_ids = [
            message.notified_partner_ids.ids
            for message in self.other_cancel_deputation.message_ids
            if message.notified_partner_ids
        ]
        for partner in notified_partner_ids:
            for partner_id in partner:
                partners.append(partner_id)
        # todo
        # self.assertIn(self.user.partner_id.id, partners)

        # Check deputation is cancaled
        self.assertEqual(self.deputation.stage_id.name, "Refused")
        self.assertEqual(self.deputation.state, "cancel")
