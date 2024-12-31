from datetime import datetime
# js_assign_outstanding_line
import pytz
from dateutil.relativedelta import relativedelta
# create_new_invoice
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
# service_line_ids
# create_new_invoice
# terminate_reservation
class HotelReservationFinishWizard(models.TransientModel):
    _name = "hotel.reservation.finish.wizard"
    _description = "Hotel Reservation Finish"

    @api.model
    def _default_date_termination(self):
        # change date termination based on hour setting
        date = fields.Datetime.now()
        reservation = self.env["hotel.reservation"].browse(
            self._context.get("default_reservation_id")
        )
        hour_setting, hour, minute = reservation.get_hour_setting()
        if hour_setting and reservation.rent in ["daily", "monthly"]:
            tz_diff = (
                fields.Datetime.now()
                .astimezone(pytz.timezone("Asia/Riyadh"))
                .replace(tzinfo=None)
                - fields.Datetime.now()
            )
            tz_diff = tz_diff.seconds / 3600
            date = fields.Datetime.now()
            
            # .replace(hour=(hour - int(tz_diff)), minute=minute, second=0)
        return date

    reservation_id = fields.Many2one("hotel.reservation", string="Reservation")
    date_termination = fields.Datetime(
        string="Termination Date", default=_default_date_termination
    )
    is_returnable = fields.Boolean(related="reservation_id.is_returnable", store=1)
    rent = fields.Selection(related="reservation_id.rent", store=1)
    origin_rent = fields.Selection(
        string="Origin Rent Type",
        selection=[("daily", "Daily"), ("monthly", "Monthly"), ("hours", "Hours")],
    )
    is_change_rent = fields.Boolean(string="Change rent")
    is_all = fields.Boolean(string="All")
    reservation_line_ids = fields.Many2many(
        "hotel.reservation.line",
        string="Rooms",
        domain=lambda self: [
            ("line_id", "=", self._context.get("active_id")),
            ("date_check_out", "=", False),
            ("date_termination", "=", False),
        ],
    )
    type = fields.Selection(
        string="type", selection=[("finish", "Finish"), ("extension", "Extension")]
    )
    duration = fields.Integer(string="Duration", default=1)
    display_button_history = fields.Boolean(
        string="Display Button history", compute="_compute_display_button_history"
    )

    def get_dates(self, rent, date, duration):
        """Get checkin and check out dates"""
        if date:
            if rent == "daily":
                checkin = date
                checkout = checkin + relativedelta(days=int(duration))
            elif self.rent == "monthly":
                checkin = date + relativedelta(days=1)
                checkout = checkin + relativedelta(days=int((self.duration * 30) - 1))
            else:
                checkin = date
                checkout = checkin + relativedelta(hours=int(duration))
            return checkin, checkout

    @api.onchange("date_termination")
    def _onchange_date_termination(self):
        """Change date termination"""
        if self.date_termination and self.reservation_id.rent != "hours":
            self.date_termination = self.date_termination
            # date termination should be by default based on setting hours
            hour_setting, hour, minute = self.reservation_id.get_hour_setting()
            if hour_setting and self.rent in ["daily", "monthly"]:
                tz_diff = (
                    self.date_termination.astimezone(
                        pytz.timezone("Asia/Riyadh")
                    ).replace(tzinfo=None)
                    - self.date_termination
                )
                tz_diff = tz_diff.seconds / 3600
                self.date_termination = self.date_termination.replace(
                    hour=(hour - int(tz_diff)), minute=minute, second=0
                )

    @api.onchange("origin_rent")
    def _onchange_origin_rent(self):
        """Change origin rent"""
        if self.origin_rent and self.rent:
            self.is_change_rent = True if self.origin_rent != self.rent else False

    # def create_new_invoice(self, history_rooms, lines, advance, invoice, payments):
    #     """create new invoice"""
    #     # update folio lines
    #     invoice.button_cancel()
    #     self.reservation_id.folio_id.order_id.action_draft()
    #     # update folio lines
    #     for room_line in self.reservation_id.folio_id.room_line_ids:
    #         if not len(history_rooms) or (
    #             len(history_rooms)
    #             and room_line.product_id.id
    #             not in history_rooms.mapped("old_room_id.product_id").ids
    #         ):
    #             room = self.env["hotel.room"].search(
    #                 [("product_id", "=", room_line.product_id.id)], limit=1
    #             )
    #             # update folio and invoice line by new date termination
    #             # get duration and date checkout
    #             checkout_date = (
    #                 room_line.reservation_line_id.date_termination
    #                 if room_line.reservation_line_id.date_termination
    #                 else room_line.reservation_line_id.date_extension
    #             )
    #             if not checkout_date:
    #                 checkout_date = self.reservation_id["checkout"]
    #             duration = (
    #                 room_line.reservation_line_id.duration_termination
    #                 if room_line.reservation_line_id.duration_termination
    #                 else room_line.reservation_line_id.duration_extension
    #             )
    #             if not duration:
    #                 duration = self.reservation_id.duration
    #             if room_line.product_uom_qty:
    #                 # update folio lines by new value (qty and price)
    #                 self.reservation_id.update_folio_invoice(
    #                     room_line,
    #                     room,
    #                     checkout_date,
    #                     duration,
    #                     self.is_change_rent,
    #                 )

    #     if len(history_rooms):
    #         # calculate discount of the change rooms
    #         self.update_discount_change_room(lines, False)
    #     # update discount and returnable amount in folio and invoice
    #     self.reservation_id._compute_total_room_rate()
    #     self.reservation_id.update_discount_insurance_returnable_folio(
    #         (self.reservation_id.discount + self.reservation_id.discount_change_room),
    #         self.reservation_id.returnable_amount,
    #         False,
    #     )
    #     # create line for advance
    #     if advance:
    #         product_id = (
    #             self.env["ir.config_parameter"]
    #             .sudo()
    #             .get_param("sale.default_deposit_product_id")
    #         )
    #         product = self.env["product.product"].browse(int(product_id))
    #         self.reservation_id.folio_id.write(
    #             {
    #                 "order_line": [
    #                     (
    #                         0,
    #                         0,
    #                         {
    #                             "name": _("Down Payment"),
    #                             "price_unit": advance,
    #                             "product_uom_qty": 1,
    #                             "order_id": self.reservation_id.folio_id.id,
    #                             "product_uom": product.uom_id.id,
    #                             "product_id": product.id,
    #                         },
    #                     )
    #                 ]
    #             }
    #         )

    #     self.reservation_id.folio_id.action_confirm()
    #     # create and post invoice
    #     if self.reservation_id.folio_id.order_id._get_invoiceable_lines():
    #         self.reservation_id.folio_id.create_invoices()
    #         self.reservation_id.folio_id.hotel_invoice_id.action_post()
    #         invoice.button_draft()
    #         invoice.button_cancel()
    #         for line_id in payments.mapped("line_ids"):
    #             self.reservation_id.folio_id.hotel_invoice_id.js_assign_outstanding_line(
    #                 line_id.id
    #             )
    #     else:
    #         # should change rent type
    #         if (
    #             not self.reservation_id.folio_id.order_id._get_invoiceable_lines()
    #             and self.reservation_id.rent == "monthly"
    #         ):
    #             self.reservation_id.folio_id.hotel_invoice_id = invoice.id
    #             raise ValidationError(_("you should change rent to daily"))
    def create_new_invoice(self, history_rooms, lines, advance, invoice, payments):
        """Create new invoice with both rent and services included."""
        # Cancel the current invoice and set the order to draft
        invoice.button_cancel()
        self.reservation_id.folio_id.order_id.action_draft()

        # Update folio lines for room rent and durations
        for room_line in self.reservation_id.folio_id.room_line_ids:
            if not history_rooms or room_line.product_id.id not in history_rooms.mapped('old_room_id.product_id').ids:
                room = self.env['hotel.room'].search([('product_id', '=', room_line.product_id.id)], limit=1)
                checkout_date = room_line.reservation_line_id.date_termination or room_line.reservation_line_id.date_extension or self.reservation_id['checkout']
                duration = room_line.reservation_line_id.duration_termination or room_line.reservation_line_id.duration_extension or self.reservation_id.duration
                if room_line.product_uom_qty:
                    self.reservation_id.update_folio_invoice(room_line, room, checkout_date, duration, self.is_change_rent)
        
        # Re-calculate discounts for changed rooms if applicable
        if history_rooms:
            self.update_discount_change_room(lines, False)

        # Update total room rate and related fields on reservation
        self.reservation_id._compute_total_room_rate()
        self.reservation_id.update_discount_insurance_returnable_folio(
            self.reservation_id.discount + self.reservation_id.discount_change_room,
            self.reservation_id.returnable_amount,
            False
        )

        # Handle advance payment
        if advance:
            product_id = self.env['ir.config_parameter'].sudo().get_param('sale.default_deposit_product_id')
            product = self.env['product.product'].browse(int(product_id))
            self.reservation_id.folio_id.write({
                'order_line': [(0, 0, {
                    'name': _('Down Payment'),
                    'price_unit': advance,
                    'product_uom_qty': 1,
                    'order_id': self.reservation_id.folio_id.id,
                    'product_uom': product.uom_id.id,
                    'product_id': product.id,
                })]
            })

        # Confirm the folio to generate a new invoice
        self.reservation_id.folio_id.action_confirm()

        # Create and post a new invoice if there are invoiceable lines
        if self.reservation_id.folio_id.order_id._get_invoiceable_lines():
            self.reservation_id.folio_id.create_invoices()
            # Add services to the new invoice
            service_lines = self.reservation_id.folio_id.service_line_ids
            for service_line in service_lines:
                new_invoice_line_vals = {
                    'product_id': service_line.product_id.id,
                    'quantity': service_line.product_uom_qty,
                    'price_unit': service_line.price_unit,
                    # Include additional fields as necessary
                }
                self.reservation_id.folio_id.hotel_invoice_id.write({'invoice_line_ids': [(0, 0, new_invoice_line_vals)]})
            self.reservation_id.folio_id.hotel_invoice_id.action_post()

            # Draft and cancel the old invoice to allow re-assigning payments
            invoice.button_draft()
            invoice.button_cancel()
            for payment in payments:
                for line_id in payment.mapped('line_ids'):
                    self.reservation_id.folio_id.hotel_invoice_id.js_assign_outstanding_line(line_id.id)
        else:
            if not self.reservation_id.folio_id.order_id._get_invoiceable_lines() and self.reservation_id.rent == 'monthly':
                # Handle case where rent type might need to be changed
                self.reservation_id.folio_id.hotel_invoice_id = invoice.id
                raise ValidationError(_("You should change the rent type to daily."))

    # flake8: noqa: C901
    def terminate_reservation(self):
        """Terminate Reservation"""
        if (
            self.reservation_id.reservation_type == "collective"
            and not self.is_all
            and not len(self.reservation_line_ids)
        ):
            raise ValidationError(_("you should choose rooms"))
        if self.reservation_id.reservation_type == "individual":
            # change state and check out of reservation
            self.reservation_id.date_termination = self.date_termination
            lines = self.reservation_id.reservation_line
            # send rating email to customers
            self.reservation_id.rated_partner_id = self.reservation_id.partner_id
            self.reservation_id.send_rating_mail_customer(
                self.reservation_id.partner_id
            )
        else:
            lines = (
                self.reservation_id.reservation_line.filtered(
                    lambda line: not line.date_termination and not line.date_check_out
                )
                if self.is_all
                else self.reservation_line_ids
            )
            # send rating email to customers
            for line_reservation in lines:
                partner = (
                    line_reservation.partner_id
                    if line_reservation.tenant == "person"
                    else line_reservation.partner_company_id
                )
                self.reservation_id.rated_partner_id = partner
                self.reservation_id.send_rating_mail_customer(partner)
        lines.write(
            {
                "date_termination": self.date_termination,
            }
        )
        for line in lines:
            # Update lines reservation in rooms and folio
            self.reservation_id.update_room_reservation_line(
                line, line.room_id, self.date_termination
            )

        if self.is_returnable:
            # create and post invoice
            if not self.reservation_id.folio_id.hotel_invoice_id:
                self.reservation_id.create_post_invoice()
            if len(
                self.reservation_id.history_room_ids.filtered(
                    lambda history: not history.is_no_calculated
                )
            ):
                # calculate discount of the change rooms
                self.update_discount_change_room(lines, True)
            # if reservation is returnable change date to of reservation and rent
            old_rent = self.rent
            old_checkin = self.reservation_id.checkin
            old_checkout = self.reservation_id.checkout
            old_duration = self.reservation_id.duration
            if self.is_change_rent:
                self.reservation_id.rent = self.origin_rent
            if self.reservation_id.reservation_type == "individual":
                # change date termination
                self.reservation_id.checkout = self.date_termination
                self.reservation_id._onchange_checkin_checkout()
                if old_rent == "daily":
                    old_unity = "Day"
                elif old_rent == "monthly":
                    old_unity = "Month"
                else:
                    old_unity = "Hour"
                if self.origin_rent == "daily":
                    unity = "Day"
                elif self.origin_rent == "monthly":
                    unity = "Month"
                else:
                    unity = "Hour"

                # prepare message
                body = _(
                    "End of Reservation  will leads to change reservation dates"
                    " from %s-%s (%s %s) to %s-%s (%s %s)"
                ) % (
                    old_checkin,
                    old_checkout,
                    old_duration,
                    old_unity,
                    self.reservation_id.checkin,
                    self.reservation_id.checkout,
                    self.reservation_id.duration,
                    unity,
                )
            else:

                if len(
                    self.reservation_id.reservation_line.filtered(
                        lambda line: line.date_termination
                    )
                ) == len(self.reservation_id.reservation_line):
                    self.reservation_id.write(
                        {
                            "checkout": max(
                                self.reservation_id.reservation_line.mapped(
                                    "date_termination"
                                )
                            )
                        }
                    )
                self.reservation_id._onchange_checkin_checkout()
                # prepare message
                body = _(
                    "End of Reservation  will leads to change reservation dates for rooms %s"
                ) % (lines.mapped("room_id.name"))
            if self.is_change_rent:
                body += _(" and to change rent type  from %s to %s") % (
                    old_rent,
                    self.origin_rent,
                )
            # post message
            self.reservation_id.message_post(body=body)
            if self.is_returnable:
                invoice = self.reservation_id.folio_id.hotel_invoice_id
                self.reservation_id.folio_id.hotel_invoice_id = False
                # get history of rooms
                history_rooms = self.reservation_id.history_room_ids.filtered(
                    lambda history: not history.is_no_calculated
                )
                # get payments
                payments_posted = self.reservation_id.payment_ids.filtered(
                    lambda payment: payment.state == "posted"
                )
                payments = self.reservation_id.payment_ids.filtered(
                    lambda payment: payment.state != "cancel"
                    and payment.payment_type == "inbound"
                    and payment.partner_type == "customer"
                )
                final_cost = (
                    self.reservation_id.final_cost - self.reservation_id.insurance
                )
                # calculate difference
                difference_payments = sum(payments.mapped("amount")) - (final_cost)
                if (
                    len(payments)
                    and self.reservation_id.final_cost
                    and (
                        (final_cost < sum(payments.mapped("amount")))
                        or (sum(payments.mapped("amount")) == invoice.amount_total)
                    )
                ):
                    # create new invoice when payment greater than final cost and create refund
                    if (final_cost < sum(payments.mapped("amount"))) and not (
                        sum(payments.mapped("amount")) == invoice.amount_total
                    ):
                        self.create_new_invoice(
                            history_rooms,
                            lines,
                            difference_payments,
                            invoice,
                            payments_posted.filtered(
                                lambda payment: payment.payment_type == "inbound"
                                and payment.partner_type == "customer"
                            ),
                        )
                        invoice = self.reservation_id.folio_id.hotel_invoice_id
                    # create reversal move
                    move_reversal = (
                        self.env["account.move.reversal"]
                        .with_context(
                            active_model="account.move", active_ids=invoice.id
                        )
                        .create(
                            {
                                "date": datetime.today().date(),
                                "refund_method": "refund",
                            }
                        )
                    )
                    reversal = move_reversal.reverse_moves()
                    reverse_move = self.env["account.move"].browse(reversal["res_id"])

                    reverse_move.invoice_line_ids.with_context(
                        check_move_validity=False
                    ).sudo().unlink()
                    reverse_move.line_ids.with_context(
                        check_move_validity=False
                    ).sudo().unlink()
                    reverse_move.write(
                        {
                            "invoice_line_ids": [
                                (
                                    0,
                                    0,
                                    {
                                        "name": _("Refund Customer"),
                                        "quantity": 1,
                                        "price_unit": difference_payments,
                                        "sale_line_ids": [
                                            (
                                                4,
                                                self.reservation_id.folio_id.order_id.order_line[
                                                    0
                                                ].id,
                                            )
                                        ],
                                    },
                                )
                            ]
                        }
                    )
                    reverse_move.with_context(
                        check_move_validity=False
                    )._onchange_invoice_line_ids()
                    # post reversed invoice
                    reverse_move.action_post()
                    self.reservation_id.folio_id.hotel_invoice_id = invoice
                    # relate payment to invoice
                    for line_id in payments_posted.filtered(
                        lambda payment: payment.payment_type == "outbound"
                    ).mapped("line_ids"):
                        reverse_move.js_assign_outstanding_line(line_id.id)
                else:
                    # cancel ancien invoice
                    if self.reservation_id.final_cost:
                        invoice.button_cancel()
                    else:
                        self.reservation_id.folio_id.hotel_invoice_id = invoice.id
                if not len(payments) or sum(payments.mapped("amount")) < final_cost:
                    # create new invoice when payment less than final cost
                    self.create_new_invoice(
                        history_rooms,
                        lines,
                        False,
                        invoice,
                        payments_posted.filtered(
                            lambda payment: payment.payment_type == "inbound"
                            and payment.partner_type == "customer"
                        ),
                    )

    @api.constrains("duration", "type")
    def _check_duration(self):
        """Check duration"""
        for reservation_extend in self:
            if (
                reservation_extend.type == "extension"
                and not reservation_extend.duration
            ):
                raise ValidationError(_("Duration should be greater than 0"))

    @api.constrains("date_termination")
    def _check_date_termination(self):
        """Check date termination"""
        for reservation_finish in self:
            if (
                reservation_finish.date_termination
                and reservation_finish.type == "finish"
            ):
                if (
                    reservation_finish.reservation_id.reservation_type == "individual"
                    and reservation_finish.date_termination
                    < reservation_finish.reservation_id.date_check_in
                ) or (
                    reservation_finish.reservation_id.reservation_type == "collective"
                    and (
                        reservation_finish.reservation_line_ids.filtered(
                            lambda reservation_line: not reservation_line.date_termination
                            and reservation_line.date_check_in
                            > reservation_finish.date_termination
                        )
                        or (
                            reservation_finish.is_all
                            and reservation_finish.reservation_id.reservation_line.filtered(
                                lambda line: not line.date_termination
                                and line.date_check_in
                                > reservation_finish.date_termination
                            )
                        )
                    )
                ):
                    raise ValidationError(
                        _("Termination Date should be greater than check in date")
                    )
                if reservation_finish.date_termination.date() < datetime.today().date():
                    raise ValidationError(
                        _("Termination Date should be greater or equal to today")
                    )
                if (
                    reservation_finish.reservation_id.reservation_type == "individual"
                    and reservation_finish.date_termination
                    > reservation_finish.reservation_id.checkout
                ) or (
                    reservation_finish.reservation_id.reservation_type == "collective"
                    and (
                        reservation_finish.reservation_line_ids.filtered(
                            lambda reservation_line: (
                                (
                                    not reservation_line.date_extension
                                    and reservation_finish.reservation_id.checkout
                                    < reservation_finish.date_termination
                                )
                                or (
                                    reservation_line.date_extension
                                    and reservation_line.date_extension
                                    < reservation_finish.date_termination
                                )
                            )
                        )
                        or (
                            reservation_finish.is_all
                            and reservation_finish.reservation_id.reservation_line.filtered(
                                lambda line: (
                                    not line.date_termination
                                    and not line.date_check_out
                                    and (
                                        (
                                            not line.date_extension
                                            and reservation_finish.reservation_id.checkout
                                            < reservation_finish.date_termination
                                        )
                                        or (
                                            line.date_extension
                                            and line.date_extension
                                            < reservation_finish.date_termination
                                        )
                                    )
                                )
                            )
                        )
                    )
                ):
                    raise ValidationError(
                        _("Termination Date should be less than check out date")
                    )

    def check_room_extension(self, room, checkin, checkout):
        """Check reservation extension."""
        if room.get_status_room_dates(self.reservation_id, checkin, checkout):
            raise ValidationError(
                _(
                    "It is not possible to extend reservation"
                    " because the room %s is not available on this date"
                )
                % room.name
            )

    def update_discount_change_room(self, lines, terminate_reservation):
        """Update Change Rooms Discount"""
        for rsv_line in lines:
            rsv_line.discount_change_room = 0
            # get history if there is no termination reservation
            history_line_rooms = self.reservation_id.history_room_ids.filtered(
                lambda history_line: not history_line.is_no_calculated
                and history_line.reservation_line_id == rsv_line
            )
            # get histoty betwwen termination dates
            if terminate_reservation and rsv_line.date_termination:
                history_line_rooms = self.reservation_id.history_room_ids.filtered(
                    lambda history_line: not history_line.is_no_calculated
                    and history_line.reservation_line_id == rsv_line
                    and history_line.change_date.date()
                    <= rsv_line.date_termination.date()
                )

            for history in history_line_rooms:
                # calculate checkin, checkout and duration of old rooms
                duration = self.reservation_id.get_duration_change_room(
                    history.reservation_date, history.change_date, self.origin_rent
                )
                before_histories = self.reservation_id.history_room_ids.filtered(
                    lambda before_history: not before_history.is_no_calculated
                    and before_history.id < history.id
                    and before_history.reservation_line_id == rsv_line
                )
                if (
                    history.reservation_date.date() == history.change_date.date()
                    and self.reservation_id.rent in ["monthly", "daily"]
                ):
                    duration = 0
                checkout = history.change_date + relativedelta(days=int(-1))
                if checkout.date() < self.reservation_id.checkin.date():
                    checkout = self.reservation_id.checkin
                if terminate_reservation and checkout > rsv_line.date_termination:
                    checkout = rsv_line.date_termination

                if (
                    before_histories
                    and duration
                    and before_histories[-1].discount_type != "no_discount"
                ):
                    # calculate discount of old rooms
                    old_room_price_unit = self.reservation_id.get_price(
                        history.old_other_price,
                        self.reservation_id.rent,
                        history.old_room_id,
                        self.reservation_id.company_id,
                        history.reservation_date,
                        checkout,
                        duration,
                    )
                    rsv_line.discount_change_room += (
                        before_histories[-1].discount
                        if before_histories[-1].discount_type != "percentage"
                        else (
                            (old_room_price_unit * duration)
                            * before_histories[-1].discount
                        )
                        / 100
                    )
            # calculate checkin, checkout and duration of last rooms in history
            if (
                history_line_rooms
                and history_line_rooms[-1].discount_type != "no_discount"
            ) and (
                not terminate_reservation
                or (
                    terminate_reservation
                    and history_line_rooms[-1].change_date.date()
                    <= rsv_line.date_termination.date()
                )
            ):
                checkout = (
                    rsv_line.date_extension
                    if rsv_line.date_extension
                    else self.reservation_id.checkout
                )
                if terminate_reservation:
                    checkout = rsv_line.date_termination
                checkin = history_line_rooms[-1].change_date
                duration = self.reservation_id.get_duration_change_room(
                    checkin, checkout, self.reservation_id.rent
                )
                if self.reservation_id.rent == "daily":
                    duration = duration + 1
                # calculate discount of new rooms
                price_unit = self.reservation_id.get_price(
                    history_line_rooms[-1].other_price,
                    self.reservation_id.rent,
                    history_line_rooms[-1].room_id,
                    self.reservation_id.company_id,
                    checkin,
                    checkout,
                    duration,
                )
                rsv_line.discount_change_room += (
                    history_line_rooms[-1].discount
                    if history_line_rooms[-1].discount_type != "percentage"
                    else ((price_unit * duration) * history_line_rooms[-1].discount)
                    / 100
                )

    def extend_reservation(self):
        """Extend Reservation"""
        if (
            self.reservation_id.reservation_type == "collective"
            and not self.is_all
            and not len(self.reservation_line_ids)
        ):
            raise ValidationError(_("you should choose rooms"))

        checkin, checkout = self.get_dates(
            self.rent, self.reservation_id.checkout, int(self.duration)
        )
        history_rooms = self.reservation_id.history_room_ids.filtered(
            lambda history: not history.is_no_calculated
        )
        folio_state = self.reservation_id.folio_id.state
        invoice_state = (
            self.reservation_id.folio_id.hotel_invoice_id.state
            if self.reservation_id.folio_id.hotel_invoice_id
            else False
        )
        payments = (
            self.env["account.payment"]
            .search([])
            .filtered(
                lambda pay: self.reservation_id.folio_id.hotel_invoice_id.id
                in pay.reconciled_invoice_ids.ids
            )
        )

        if self._context.get("default_type_reservation") == "individual":
            for room in self.reservation_id.reservation_line.mapped("room_id"):
                # check avaibility rooms
                self.check_room_extension(room, checkin, checkout)
            # set folio and invoice to draft
            self.reservation_id.write({"checkout": checkout})
            self.reservation_id._onchange_checkin_checkout()
            self.reservation_id.set_folio_draft()
            lines = self.reservation_id.reservation_line
            for room_line in self.reservation_id.folio_id.room_line_ids:
                if not len(history_rooms) or (
                    len(history_rooms)
                    and room_line.product_id.id
                    not in history_rooms.mapped("old_room_id.product_id").ids
                ):
                    room = self.env["hotel.room"].search(
                        [("product_id", "=", room_line.product_id.id)], limit=1
                    )
                    # update folio and invoice line by new date extension
                    if room_line.product_uom_qty:
                        self.reservation_id.update_folio_invoice(
                            room_line,
                            room,
                            checkout,
                            (room_line.product_uom_qty + self.duration),
                            False,
                        )
        else:
            lines = (
                self.reservation_id.reservation_line.filtered(
                    lambda line: not line.date_termination and not line.date_check_out
                )
                if self.is_all
                else self.reservation_line_ids
            )
            for line in lines:
                # update date extension and uration of reservation lines
                self.check_room_extension(line.room_id, checkin, checkout)
                if line.date_extension:
                    checkin, checkout = self.get_dates(
                        self.rent, line.date_extension, int(self.duration)
                    )
                else:
                    checkin, checkout = self.get_dates(
                        self.rent, self.reservation_id.checkout, int(self.duration)
                    )
                line.date_extension = checkout
            self.reservation_id._compute_total_room_rate()
            self.reservation_id.set_folio_draft()
            # update folio and invoice line by new date extension of lines
            for room_line in self.reservation_id.folio_id.room_line_ids:
                if (
                    room_line.reservation_line_id.date_extension
                    and not room_line.reservation_line_id.date_termination
                    and not room_line.reservation_line_id.date_check_out
                    and (
                        self.is_all
                        or (
                            room_line.reservation_line_id.id
                            in self.reservation_line_ids.ids
                            and not self.is_all
                        )
                    )
                ):
                    if not len(history_rooms) or (
                        len(history_rooms)
                        and room_line.product_id.id
                        not in history_rooms.mapped("old_room_id.product_id").ids
                    ):
                        room = self.env["hotel.room"].search(
                            [("product_id", "=", room_line.product_id.id)]
                        )
                        if room_line.product_uom_qty:
                            self.reservation_id.update_folio_invoice(
                                room_line,
                                room,
                                room_line.reservation_line_id.date_extension,
                                room_line.product_uom_qty + self.duration,
                                False,
                            )
        if len(history_rooms):
            # calculate discount of the change rooms
            self.update_discount_change_room(lines, False)
        # update discount and returnable amount in folio and invoice
        self.reservation_id._compute_total_room_rate()
        self.reservation_id.update_discount_insurance_returnable_folio(
            (self.reservation_id.discount + self.reservation_id.discount_change_room),
            self.reservation_id.returnable_amount,
            False,
        )
        # post and confirm sale and invoice
        self.reservation_id.post_folio_invoice(folio_state, invoice_state, payments)

    def button_history_details(self):
        return {
            "name": _("Room Change History"),
            "res_model": "reservation.room.change.history",
            "view_mode": "tree",
            "domain": [("reservation_id", "=", self.reservation_id.id)],
            "type": "ir.actions.act_window",
            "target": "new",
        }

    def _compute_display_button_history(self):
        for reservation_extension in self:
            reservation_extension.display_button_history = False
            if (
                reservation_extension.type == "extension"
                and reservation_extension.reservation_id.reservation_type
                == "collective"
                and not reservation_extension.is_all
                and len(reservation_extension.reservation_id.history_room_ids)
            ):
                reservation_extension.display_button_history = True
