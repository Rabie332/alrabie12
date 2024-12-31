from datetime import date

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import Form
from odoo.tools import mute_logger

from .common import TestHrInfractionBase


class TestHrInfractionFlow(TestHrInfractionBase):
    @mute_logger("odoo.addons.base.models.ir_model", "odoo.models")
    def test_hr_infraction_request_flow(self):
        # ----------------------------------------
        # Infraction Flow
        # ----------------------------------------

        # Create hr infraction type with type of amount
        self.hr_infraction_type_amount = (
            self.env["request.type"]
            .with_user(self.user_infraction_manager)
            .create(
                {
                    "name": "infraction type amount",
                    "infraction_type": "amount",
                    "code": self.env["ir.sequence"].next_by_code("request.type.seq"),
                    "res_model": "hr.infraction",
                    "res_model_id": self.env.ref(
                        "hr_infraction.model_hr_infraction"
                    ).id,
                }
            )
        )

        # Create hr infraction type with type of number_of_days
        self.hr_infraction_type_nb_days = (
            self.env["request.type"]
            .with_user(self.user_infraction_manager)
            .create(
                {
                    "name": "infraction type nb days",
                    "infraction_type": "nb_days",
                    "code": self.env["ir.sequence"].next_by_code("request.type.seq"),
                    "res_model": "hr.infraction",
                    "res_model_id": self.env.ref(
                        "hr_infraction.model_hr_infraction"
                    ).id,
                }
            )
        )

        # Get the current period
        current_month_first_day = date(
            fields.date.today().year, fields.date.today().month, 1
        )
        hr_infraction_period = self.env["hr.period"].search(
            [("date_start", "=", current_month_first_day)], limit=1
        )

        # Create infraction and test business functions
        infraction_object = self.env["hr.infraction"].with_user(
            self.user_infraction_manager
        )
        infarction_form = Form(infraction_object)
        infarction_form.employee_id = self.employee
        infarction_form.period_id = hr_infraction_period
        infarction_form.stage_id = self.env.ref(
            "hr_infraction.hr_infraction_stage_draft"
        )

        # if type is nb days check start date must be anterior to end date.
        infarction_form.request_type_id = self.hr_infraction_type_nb_days
        infarction_form.date_from = date(
            fields.date.today().year, fields.date.today().month, 2
        )
        with self.assertRaises(ValidationError):
            infarction_form.date_to = date(
                fields.date.today().year, fields.date.today().month, 1
            )

        # if type of amount check amount should be greater than zero
        infarction_form.request_type_id = self.hr_infraction_type_amount
        infarction_form.amount = 0
        with self.assertRaises(ValidationError):
            self.infraction = infarction_form.save()

        # Add amount 100
        infarction_form.amount = 100
        self.infraction = infarction_form.save()

        self.infraction.with_user(self.user_infraction_manager).action_send()
        self.infraction.with_user(self.user_infraction_manager).action_accept()
        self.assertEqual(self.infraction.state, "done", "The state must be 'done'")
