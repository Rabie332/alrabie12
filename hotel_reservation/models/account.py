from odoo import api, fields, models


class AccountPayments(models.Model):
    _inherit = "account.payment"

    reservation_id = fields.Many2one("hotel.reservation", "Reservation")
    support_type_id = fields.Many2one("account.payment.support.type", required=True)
    transaction_number = fields.Char(string="Transaction Number")
    promissory_number = fields.Char()
    promissory_due_date = fields.Date()

    def print_payment_receipt(self):
        return self.env.ref("account.action_report_payment_receipt").report_action(self)

    def action_post(self):
        res = super(AccountPayments, self).action_post()
        # relate payment created to invoice of reservation
        for payment in self:
            move_lines = payment.line_ids
            if (
                payment.reservation_id
                and payment.reservation_id.folio_id
                and payment.reservation_id.folio_id.hotel_invoice_id
            ):
                # relate payment to invoice
                if payment.payment_type == "inbound":
                    invoice = payment.reservation_id.folio_id.hotel_invoice_id
                else:
                    invoice = (
                        payment.reservation_id.folio_id.hotel_invoice_id.reversal_move_id
                    )
                if invoice:
                    for line in move_lines:
                        invoice.js_assign_outstanding_line(line.id)
                # if (
                #     payment.reservation_id.state == "done"
                #     and not payment.reservation_id.balance
                # ):
                #     payment.reservation_id.state = "finish"
        return res


class AccountMove(models.Model):
    _inherit = "account.move"

    is_no_refund = fields.Boolean(string="No Refund")

    @api.model
    def create(self, vals):
        res = super(AccountMove, self).create(vals)
        if self._context.get("folio_id"):
            folio = self.env["hotel.folio"].browse(self._context["folio_id"])
            if (
                folio
                and (
                    not folio.is_returnable
                    and (
                        not folio.reservation_id.history_room_ids
                        or folio.reservation_id.history_room_ids
                        and folio.reservation_id.history_room_ids.filtered(
                            lambda history: history.is_no_calculated
                            and (
                                folio.reservation_id.rent == "daily"
                                and history.old_room_id.list_price
                                > history.room_id.list_price
                            )
                            or (
                                folio.reservation_id.rent == "monthly"
                                and history.old_room_id.monthly_price
                                > history.room_id.monthly_price
                            )
                            or folio.reservation_id.rent == "hours"
                            and history.old_room_id.hourly_price
                            > history.room_id.hourly_price
                        )
                    )
                )
                and folio.reservation_id.state != "cancel"
            ):
                res.is_no_refund = True
        return res

    def action_post(self):
        res = super(AccountMove, self).action_post()
        # relate payment created from reservation to invoice of reservation
        for move in self:
            if move.reservation_id:
                payments = move.reservation_id.payment_ids.filtered(
                    lambda payment_reservation: payment_reservation.payment_type
                    == "inbound"
                    and payment_reservation.state == "posted"
                )
                for payment in payments:
                    move_lines = payment.line_ids.filtered(
                        lambda line: line.account_internal_type
                        in ("receivable", "payable")
                        and not line.reconciled
                    )
                    # flake8: noqa: B950
                    for line in move_lines:
                        payment.reservation_id.folio_id.hotel_invoice_id.js_assign_outstanding_line(
                            line.id
                        )
        return res


class AccountPaymentRegister(models.TransientModel):
    _inherit = "account.payment.register"

    reservation_id = fields.Many2one("hotel.reservation", "Reservation")
    support_type_id = fields.Many2one("account.payment.support.type")
    promissory_number = fields.Char()
    promissory_due_date = fields.Date()

    def _create_payment_vals_from_wizard(self):
        payment_vals = super(
            AccountPaymentRegister, self
        )._create_payment_vals_from_wizard()
        # update support type of payment based on payment register
        payment_vals.update(
            {
                "support_type_id": self.support_type_id.id,
                "promissory_number": self.promissory_number,
                "promissory_due_date": self.promissory_due_date,
            }
        )
        return payment_vals

    def _create_payments(self):
        payments = super(AccountPaymentRegister, self)._create_payments()
        if self._context.get("active_model") == "account.move":
            # link the reservation to the invoice
            invoice = self.env["account.move"].browse(
                self._context.get("active_id", [])
            )
            if invoice.reservation_id:
                payments.write({"reservation_id": invoice.reservation_id.id})
        return payments


class AccountPaymentSupportType(models.Model):
    _name = "account.payment.support.type"
    _description = "Support Types"

    name = fields.Char(string="Name", translate=1)
    active = fields.Boolean(default=True)
    support_type = fields.Selection([("inbound", "Inbound"), ("outbound", "Outbound")])
