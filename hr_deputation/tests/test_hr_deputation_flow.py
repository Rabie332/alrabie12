from datetime import date

from odoo.exceptions import ValidationError
from odoo.tests import Form
from odoo.tools import mute_logger, relativedelta

from .common import TestHrDeputationBase


class TestHrDeputationFlow(TestHrDeputationBase):
    @mute_logger("odoo.addons.base.models.ir_model", "odoo.models")
    def test_hr_deputation_request_flow(self):
        # ----------------------------------------
        # deputation Flow
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

        # check user and user_manager are followers of this request

        self.assertIn(
            self.user_manager.partner_id,
            self.deputation.message_partner_ids,
            "Deputation manager is not added as a request followers.",
        )
        self.assertIn(
            self.user.partner_id,
            self.deputation.message_partner_ids,
            "User is not added as a request followers.",
        )

        # check the next activity is correct (activity's name and its assigned to right user)

        self.assertEqual(
            self.deputation.activity_type_id.name, "Deputation is ready to be approved"
        )
        self.assertEqual(
            self.deputation.activity_ids[0].user_id,
            self.user_manager,
            "Activity should be assigned to Deputation manager.",
        )

        # check the request has the right stage and state

        self.assertEqual(self.deputation.stage_id.name, "Validate")
        self.assertEqual(self.deputation.state, "in_progress")

        # accept request by user_manager

        self.deputation.with_user(self.user_manager).action_accept()

        # check the name of stage and state.

        self.assertEqual(self.deputation.stage_id.name, "Done")
        self.assertEqual(self.deputation.state, "done")

        # employee should receive an email notification of approved request
        partners = [
            message.user_id.partner_id.id
            for message in self.deputation.activity_ids
            if message.sudo().user_id.partner_id
        ]
        self.assertIn(self.employee.user_id.partner_id.id, partners)

        # Create another public holiday and test business functions
        # Test constraint _check_date : Dates overlap with a previous holiday

        other_deputation_form = Form(deputation_object)

        other_deputation_form.employee_id = self.employee
        other_deputation_form.request_type_id = self.deputation_type_mission
        other_deputation_form.date_from = date.today() + relativedelta(days=-1)
        other_deputation_form.date_to = date.today() + relativedelta(days=+1)
        other_deputation_form.task_name = "Work mission"
        other_deputation_form.city_id = self.riadh_city
        other_deputation_form.stage_id = self.stage_send
        other_deputation_form.read_reviewed_policies_regulations = True
        self.other_deputation = other_deputation_form.save()

        # test constraint _check_dates: date_from should be smaller than date_to

        with self.assertRaises(ValidationError):
            self.other_deputation.write(
                {"date_from": date(2020, 4, 4), "date_to": date(2020, 4, 3)}
            )

        # test constraint _check_duration: The annual deputation balance has been exceeded!

        with self.assertRaises(ValidationError):
            self.other_deputation.write({"duration": 31})

        # test constraint check_intersection: There is an overlap of dates with a deputation

        with self.assertRaises(ValidationError):
            self.other_deputation.write(
                {
                    "date_from": date.today() + relativedelta(days=+9),
                    "date_to": date.today() + relativedelta(days=+10),
                }
            )

        # Test Refuse workflow : refuse other_deputation  by officer

        # Send the request with user

        self.other_deputation.with_user(self.user).action_send()

        # Refuse request by officer

        self.other_deputation.with_user(self.user_officer).action_refuse()

        # check request has the right stage and state

        self.assertEqual(self.other_deputation.stage_id.name, "Refused")
        self.assertEqual(self.other_deputation.state, "cancel")

        # User should receive an email notification of refused request
        partners = [
            message.user_id.partner_id.id
            for message in self.deputation.activity_ids
            if message.sudo().user_id.partner_id
        ]
        self.assertIn(self.user.partner_id.id, partners)
