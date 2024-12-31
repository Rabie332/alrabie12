from odoo import _, api, fields, models

# is_paid
class HrPaymentRequest(models.Model):
    _name = "hr.payment.request"
    _inherit = "request"
    _description = "Hr Payment Request"

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Fields
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    statement = fields.Text(
        "Statement", readonly=1, states={"draft": [("readonly", 0)]}
    )
    active = fields.Boolean("Active", default=True)
    amount = fields.Float("Amount", readonly=1, states={"draft": [("readonly", 0)]})
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        index=True,
        default=lambda self: self.env.company,
    )
    payment_id = fields.Many2one(
        "account.payment", "Payment", readonly=True, copy=False
    )
    is_paid = fields.Boolean("Is Paid", copy=False)

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # ORM Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    @api.model
    def create(self, values):
        payment = super(HrPaymentRequest, self).create(values)
        payment.name = self.env["ir.sequence"].next_by_code("hr.payment.request.seq")
        return payment

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Compute Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    @api.depends("stage_id")
    def _compute_display_button(self):
        for rec in self:
            users = rec._get_approvers()
            rec.display_button_refuse = False
            rec.display_button_accept = False
            rec.display_button_send = False
            if rec.state == "draft" and (
                (rec.create_uid and rec.create_uid.id == rec.env.uid)
                or rec.env.user.has_group("hr.group_hr_manager")
            ):
                rec.display_button_send = True
            elif rec.state == "in_progress" and (
                rec.env.uid in users or rec.env.user.has_group("hr.group_hr_manager")
            ):
                rec.display_button_accept = True
                rec.display_button_refuse = True

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Onchange Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def _sync_employee_details(self):
        for request in self:
            super(HrPaymentRequest, request)._sync_employee_details()
            request.company_id = request.employee_id.company_id.id

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Business Methods
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def button_payment_order(self):

        total = self.amount
        journal = self.env["account.payment"]._get_default_journal()
        payment_methods = (
            (total > 0)
            and journal.inbound_payment_method_ids
            or journal.outbound_payment_method_ids
        )
        currency = journal.currency_id or self.company_id.currency_id
        payment = self.env["account.payment"].create(
            {
                "payment_method_id": payment_methods and payment_methods[0].id or False,
                "payment_type": total > 0 and "outbound",
                "partner_type": "supplier",
                "partner_id": self.employee_id.user_id.partner_id.id
                if self.employee_id.user_id
                else False,
                "journal_id": journal.id,
                "state": "draft",
                "currency_id": currency.id,
                "amount": total,
                "ref": _("Payment Request")
                + str(self.name)
                + ":"
                + str(self.employee_id.name),
            }
        )
        self.payment_id = payment.id
        return {
            "type": "ir.actions.act_window",
            "res_model": "account.payment",
            "view_mode": "form",
            "res_id": payment.id,
        }
