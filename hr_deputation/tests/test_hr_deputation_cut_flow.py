from datetime import date

from odoo.tests import Form
from odoo.tools import mute_logger, relativedelta

from .common import TestHrDeputationBase


class TestHrDeputationCutFlow(TestHrDeputationBase):
    @mute_logger("odoo.addons.base.models.ir_model", "odoo.models")
    def test_hr_deputation_cut_request_flow(self):
        # ----------------------------------------
        # Cut a deputation request that is in the future
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

        self.send_cuttation = self.env.ref("hr_deputation.hr_deputation_cut_stage_send")
        self.validate_cuttation = self.env.ref(
            "hr_deputation.hr_deputation_cut_stage_validate"
        )
        self.validate_cuttation.write(
            {"assign_type": "user", "default_user_id": self.user_manager}
        )
        # Create cuttation request and refuse it by deputation manager

        cuttation_vals = {}
        context = self.deputation.button_cut()["context"]
        cuttation_vals["employee_id"] = context["default_employee_id"]
        cuttation_vals["date_from"] = context["default_date_from"]
        cuttation_vals["date_to"] = context["default_date_to"]
        cuttation_vals["duration"] = context["default_duration"]
        cuttation_vals["deputation_id"] = context["default_deputation_id"]
        cuttation_vals["cut_date"] = date.today()
        cuttation_vals["reason_cut"] = "Cuttation reason"
        cuttation_vals["stage_id"] = self.send_cuttation.id
        self.cut_deputation = (
            self.env["hr.deputation.cut"]
            .with_user(self.user)
            .create(cuttation_vals.copy())
        )

        # user sends his request.

        self.cut_deputation.with_user(self.user).action_send()

        # check user and user_manager are followers of this request

        self.assertIn(
            self.user_manager.partner_id,
            self.cut_deputation.message_partner_ids,
            "Deputation manager is not added as a cuttation request followers.",
        )
        self.assertIn(
            self.user.partner_id,
            self.cut_deputation.message_partner_ids,
            "User is not added as a cuttation request followers.",
        )

        # check the next activity is correct (activity's name and its assigned to right user)

        self.assertEqual(
            self.cut_deputation.activity_type_id.name,
            "Deputation Cut is ready to be approved",
        )
        self.assertEqual(
            self.cut_deputation.activity_ids[0].user_id,
            self.user_manager,
            "Activity should be assigned to Deputation manager.",
        )

        # check the request has the right stage and state

        self.assertEqual(self.cut_deputation.stage_id.name, "Validate")
        self.assertEqual(self.cut_deputation.state, "in_progress")

        # Refuse request by officer

        self.cut_deputation.with_user(self.user_manager).action_refuse()

        # check request has the right stage and state

        self.assertEqual(self.cut_deputation.stage_id.name, "Refused")
        self.assertEqual(self.cut_deputation.state, "cancel")

        # User should receive an email notification of refused request
        partners = []
        notified_partner_ids = [
            message.notified_partner_ids.ids
            for message in self.cut_deputation.message_ids
            if message.notified_partner_ids
        ]
        for partner in notified_partner_ids:
            for partner_id in partner:
                partners.append(partner_id)
        # todo
        # self.assertIn(self.user.partner_id.id, partners)

        # Create cuttation request and accept it by officer

        self.other_cut_deputation = (
            self.env["hr.deputation.cut"]
            .with_user(self.user)
            .create(cuttation_vals.copy())
        )

        # user sends his request.

        self.other_cut_deputation.with_user(self.user).action_send()

        # Get the token_deputation_sum to check it after action_accept
        sum_before_cutting = self.deputation_stock.token_deputation_sum

        # accept request by user_officer
        self.other_cut_deputation.with_user(self.user_officer).action_accept()

        # Check deputation_stock.token_deputation_sum has subtracted remaining_duration
        self.assertEqual(
            self.deputation_stock.token_deputation_sum,
            sum_before_cutting - self.other_cut_deputation.remaining_duration,
        )

        # check the name of stage and state.

        self.assertEqual(self.other_cut_deputation.stage_id.name, "Done")
        self.assertEqual(self.other_cut_deputation.state, "done")

        # employee should receive an email notification of approved request
        partners = []
        notified_partner_ids = [
            message.notified_partner_ids.ids
            for message in self.other_cut_deputation.message_ids
            if message.notified_partner_ids
        ]
        for partner in notified_partner_ids:
            for partner_id in partner:
                partners.append(partner_id)
        # todo
        # self.assertIn(self.user.partner_id.id, partners)
