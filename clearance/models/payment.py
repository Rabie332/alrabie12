import json

from dateutil.relativedelta import relativedelta
from lxml import etree

from odoo import _, api, fields, models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    clearance_request_id = fields.Many2one(
        "clearance.request", string="Clearance Request"
    )
    code_supplier = fields.Char(string="Code ")
    pay_number = fields.Char(string="Pay Number")
    attachment_count = fields.Integer(
        string="Attachments number",
        compute="_compute_attachment_count",
    )
    request_number = fields.Char("Request Number", related="clearance_request_id.name")

    # ------------------------------------------------------
    # ORM Methods
    # ------------------------------------------------------
    @api.model
    def create(self, vals):
        """Related every payment by clearance."""
        payment = super(AccountPayment, self).create(vals)
        if payment.clearance_request_id and not payment.ref:
            payment.ref = (
                _("Operation Number") + " " + str(payment.clearance_request_id.name)
            )
        if self._context.get("default_payment_fees"):
            payment.clearance_request_id.payment_fees_id = payment.id
        if self._context.get("default_payment_insurance"):
            payment.clearance_request_id.payment_insurance_id = payment.id
        if self._context.get("default_payment_fees_statement"):
            payment.clearance_request_id.payment_fees_statement_id = payment.id
        if self._context.get("default_payment_fees_customs_id"):
            customs_payment = self.env["clearance.request.customs.payment"].browse(
                int(self._context.get("default_payment_fees_customs_id"))
            )
            customs_payment.payment_customs_id = payment.id
        return payment

    # ------------------------------------------------------------
    # Compute methods
    # ------------------------------------------------------------

    def _compute_attachment_count(self):
        for payment in self:
            payment.attachment_count = payment.env["ir.attachment"].search_count(
                [("res_model", "=", payment._name), ("res_id", "in", payment.ids)]
            )

    # ------------------------------------------------------
    # Onchange Method
    # ------------------------------------------------------

    @api.onchange("partner_id", "payment_method_id")
    def _onchange_partner_payment(self):
        if self.partner_id:
            self.code_supplier = self.partner_id.code_partner

    @api.onchange(
        "payment_method_id",
    )
    def _onchange_payment_method_id(self):
        if self.payment_method_id and self.payment_method_id not in [
            self.env.ref("clearance.account_payment_method_pay_in"),
            self.env.ref("clearance.account_payment_method_pay_out"),
        ]:
            self.code_supplier = False
            self.pay_number = False

    # ------------------------------------------------------
    # Business Methods
    # ------------------------------------------------------

    def attachment_tree_view(self):
        """Get attachments for this object."""
        attachment_action = self.env.ref("base.action_attachment")
        action = attachment_action.sudo().read()[0]
        action["context"] = {
            "default_res_model": "account.payment",
            "default_res_id": self.ids[0],
        }
        action["domain"] = str(
            ["&", ("res_model", "=", self._name), ("res_id", "in", self.ids)]
        )
        return action

    @api.model
    def send_mail_payment_fees(self):
        today = fields.Date.from_string(fields.Date.today())
        payments = self.sudo().search(
            [
                ("state", "!=", "posted"),
            ]
        )
        users = self.env["res.users"].search(
            [("groups_id", "in", self.env.ref("account.group_account_manager").id)]
        )
        for payment in payments:
            if (payment.date - relativedelta(days=1)) == today:
                # send mail to users
                for user in users:
                    mail = (
                        self.env["mail.mail"]
                        .sudo()
                        .create(
                            {
                                "subject": _("Fees Payment"),
                                "body_html": _(
                                    "There is a payment %s with amount %s, please pay it"
                                )
                                % (payment.name, payment.amount),
                                "email_to": user.email,
                            }
                        )
                    )
                    mail.sudo().send()

    @api.model
    def fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        """fields_view_get to not change account destination."""
        res = super(AccountPayment, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu
        )
        doc = etree.XML(res["arch"])
        if self.env.context.get("default_payment_insurance"):
            for node in doc.xpath("//field[@name='destination_account_id']"):
                modifiers = json.loads(node.get("modifiers"))
                modifiers["readonly"] = True
                node.set("modifiers", json.dumps(modifiers))
            for node in doc.xpath("//field[@name='is_internal_transfer']"):
                modifiers = json.loads(node.get("modifiers"))
                modifiers["readonly"] = True
                node.set("modifiers", json.dumps(modifiers))
        res["arch"] = etree.tostring(doc, encoding="unicode")
        return res
