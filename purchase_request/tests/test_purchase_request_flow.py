from odoo.exceptions import ValidationError
from odoo.tests import Form
from odoo.tools import mute_logger

from .common import TestPurchaseRequestBase


class TestPurchaseRequestFlow(TestPurchaseRequestBase):
    @mute_logger("odoo.addons.base.models.ir_model", "odoo.models")
    def test_purchase_request_flow(self):
        # create stage done and stage refuse
        self.env["request.stage"].create(
            {
                "name": "Done",
                "res_model_id": self.env["ir.model"]._get("purchase.request").id,
                "sequence": 3,
                "res_model": "purchase.request",
                "state": "done",
            }
        )
        self.env["request.stage"].create(
            {
                "name": "Refuse",
                "res_model_id": self.env["ir.model"]._get("purchase.request").id,
                "sequence": 4,
                "res_model": "purchase.request",
                "state": "cancel",
            }
        )

        # create product

        category = self.env["product.category"].create({"name": "category"})
        product = self.env["product.product"].create(
            {"name": "product1", "type": "consu", "categ_id": category.id}
        )

        # employee requests to purchase a product

        request_object = self.env["purchase.request"].with_user(self.user)
        with self.assertRaises(ValidationError):
            # ----------------------------------------------------------------
            # Case1: estimated budget > budget of type => should crash
            # -----------------------------------------------------------------
            request_form = Form(request_object)
            request_form.estimated_budget = 6000
            request_form.description = "purchase"
            request_form.request_type_id = self.env.ref(
                "purchase_request.purchase_request_type_direct_purchase"
            )
            with request_form.line_ids.new() as line:
                line.product_id = product
                line.product_qty = 3

            request_form.save()
        # ----------------------------------------------------------------
        # Case2: estimated budget <= budget of type => it 's ok
        # ----------------------------------------------------------------

        request_form = Form(request_object)
        request_form.estimated_budget = 5000
        request_form.description = "purchase"
        request_form.request_type_id = self.env.ref(
            "purchase_request.purchase_request_type_direct_purchase"
        )
        purchase_request = request_form.save()

        # check request has the right stage and state

        self.assertEqual(purchase_request.stage_id.state, "draft")
        self.assertEqual(purchase_request.state, "draft")

        # user sends his request.
        with self.assertRaises(ValidationError):
            # ----------------------------------------------------------------
            # Case3: no product in lines => should crash
            # -----------------------------------------------------------------

            purchase_request.with_user(self.user).action_send()

        # ----------------------------------------------------------------
        # Case4: product in lines => it 's ok
        # -----------------------------------------------------------------
        with request_form.line_ids.new() as line:
            line.product_id = product
            line.product_qty = 3
        purchase_request = request_form.save()
        purchase_request.with_user(self.user).action_send()

        # check user and purchase_user are followers of this request

        self.assertIn(
            self.user_purchase.partner_id,
            purchase_request.message_partner_ids,
            "User purchase is added as a request followers.",
        )
        self.assertIn(
            self.user.partner_id,
            purchase_request.message_partner_ids,
            "User is  added as a request followers.",
        )

        # check the next activity is correct
        # activity category and its assigned to right user

        # self.assertEqual(purchase_request.activity_type_id.category, "validation")
        # self.assertEqual(
        #     purchase_request.activity_type_id.res_model_id,
        #     self.env["ir.model"]._get("purchase.request"),
        # )
        self.assertEqual(
            purchase_request.activity_type_id.name,
            "Purchase Request Approval",
        )
        self.assertEqual(
            purchase_request.activity_ids[0].user_id,
            self.user_purchase,
            "Activity should be assigned to User Purchase.",
        )

        # check the request has the right stage and state

        self.assertEqual(purchase_request.stage_id.name, "Direct manager")
        self.assertEqual(purchase_request.state, "in_progress")

        # accept request by user_purchase
        # we have three in progress stages , so we lunch accept thrice
        purchase_request.with_user(self.user_purchase).action_accept()
        purchase_request.with_user(self.user_purchase).action_accept()
        purchase_request.with_user(self.user_purchase).action_accept()
        purchase_request.with_user(self.user_purchase).action_accept()

        # check  stage and state.

        self.assertEqual(purchase_request.stage_id.state, "done")
        self.assertEqual(purchase_request.state, "done")

        # Test Refuse workflow : create request and refuse it by user purchase

        other_purchase_request_form = Form(request_object)
        other_purchase_request_form.estimated_budget = 4000
        other_purchase_request_form.description = "Other purchase"
        other_purchase_request_form.request_type_id = self.env.ref(
            "purchase_request.purchase_request_type_direct_purchase"
        )
        with other_purchase_request_form.line_ids.new() as other_line:
            other_line.product_id = product
            other_line.product_qty = 5
        other_purchase_request = other_purchase_request_form.save()

        # Send the new request with user

        other_purchase_request.with_user(self.user).action_send()

        # Refuse request by user_purchase

        other_purchase_request.with_user(self.user_purchase).action_refuse()

        # Check if activity type request approval close.

        self.assertFalse(other_purchase_request.activity_type_id)

        # check request has the right stage and state

        self.assertEqual(other_purchase_request.stage_id.state, "cancel")
        self.assertEqual(other_purchase_request.state, "cancel")
