from datetime import datetime, time

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HotelReservationCheckWizard(models.TransientModel):
    _name = "hotel.reservation.check.wizard"
    _description = "Hotel Reservation Check"

    @api.model
    def _get_domain(self):
        """Get rooms domains"""
        domain = [("line_id", "=", self._context.get("active_id"))]
        if self.env.context.get("default_check_type") == "in":
            return domain + ([("date_check_in", "=", False)])
        else:
            return [("id", "in", self._context.get("default_reservation_line_ids"))]

    reservation_id = fields.Many2one("hotel.reservation", string="Reservation")
    is_all = fields.Boolean(string="All")
    reservation_line_ids = fields.Many2many(
        "hotel.reservation.line", string="Rooms", domain=_get_domain
    )
    check_type = fields.Selection(
        string="Check type", selection=[("in", "IN"), ("out", "out")]
    )

    def action_check_in(self):
        """Action Check in."""
        if not self.is_all and not len(self.reservation_line_ids):
            raise ValidationError(_("you should choose rooms"))
        lines = (
            self.reservation_id.reservation_line.filtered(
                lambda line: not line.date_check_in
            )
            if self.is_all
            else self.reservation_line_ids
        )
        lines.write({"date_check_in": datetime.today()})
        for line in lines:
            partner = (
                line.partner_id if line.tenant == "person" else line.partner_company_id
            )
            partner.sudo().last_room_id = line.room_id.id
        # create and post invoice
        if not self.reservation_id.folio_id.hotel_invoice_id:
            self.reservation_id.create_post_invoice()

    def action_check_out(self):
        """Action Check out."""
        if not self.is_all and not len(self.reservation_line_ids):
            raise ValidationError(_("you should choose rooms"))
        # create and post invoice
        if not self.reservation_id.folio_id.hotel_invoice_id:
            self.reservation_id.create_post_invoice()
        today = datetime.today().date()
        lines = (
            self.reservation_id.reservation_line.filtered(
                lambda line: not line.date_check_out
                and (
                    (line.date_termination and line.date_termination.date() <= today)
                    or (
                        not line.date_termination
                        and (
                            (
                                self.reservation_id.checkout.date() <= today
                                and not line.date_extension
                            )
                            or (
                                line.date_extension
                                and line.date_extension.date() <= today
                            )
                        )
                    )
                )
            )
            if self.is_all
            else self.reservation_line_ids
        )
        lines.mapped("room_id").write({"is_clean": False, "status": "available"})
        self.reservation_id.create_housekeeping(lines.mapped("room_id"))
        # change state to finish when balance is 0
        if (
            len(
                self.reservation_id.reservation_line.filtered(
                    lambda line: line.date_termination and line.date_check_out
                )
            )
            == len(self.reservation_id.reservation_line)
            and not self.reservation_id.balance
        ):
            self.reservation_id.state = "finish"
        # send rating email to customers
        payments = self.reservation_id.payment_ids.filtered(
            lambda payment_reservation: payment_reservation.payment_type == "inbound"
            and payment_reservation.state == "posted"
        )
        for line in lines:
            checkout = (
                line.date_extension
                if line.date_extension
                else self.reservation_id.checkout
            )
            if line.date_termination:
                checkout = line.date_termination
            line.date_check_out = datetime.today()
            # create payment outbound or inbound if hours check out exceed setting hours
            hour_setting = self.env["hotel.reservation.setting"].search(
                [("company_id", "=", self.reservation_id.company_id.id)], limit=1
            )
            if hour_setting and hour_setting.hours_day:
                hour, minute = self.reservation_id.get_hour_minute_float(
                    hour_setting.hours_day
                )
                if self.reservation_id.rent == "daily" and (
                    line.date_check_out.date() > checkout.date()
                    or (
                        line.date_check_out.date() == checkout.date()
                        and self.reservation_id._format_date(
                            str(line.date_check_out)
                        ).time()
                        > time(hour, minute, 0)
                    )
                ):
                    if line.date_extension:
                        checkin, checkout = self.env[
                            "hotel.reservation.finish.wizard"
                        ].get_dates(self.reservation_id.rent, line.date_extension, 1)
                    else:
                        checkin, checkout = self.env[
                            "hotel.reservation.finish.wizard"
                        ].get_dates(
                            self.reservation_id.rent, self.reservation_id.checkout, 1
                        )
                    line.date_extension = checkout
                    self.reservation_id._compute_total_room_rate()
                    if self.reservation_id.folio_id.state != "draft":
                        self.reservation_id.set_folio_draft()
                        room_line = self.reservation_id.folio_id.room_line_ids.filtered(
                            lambda room_line: room_line.product_id
                            == line.room_id.product_id
                        )
                        self.reservation_id.update_folio_invoice_qty(room_line)

            partner = (
                line.partner_id if line.tenant == "person" else line.partner_company_id
            )
            partner.sudo().last_room_id = False
            self.reservation_id.rated_partner_id = partner
            self.reservation_id.send_rating_mail_customer(partner)
        # post and confirm sale and invoice
        # create payment outbound or inbound if balance is not 0
        if self.reservation_id.folio_id.state == "draft":
            self.reservation_id.post_folio_invoice("sale", "posted", payments)
        if (
            self.reservation_id.balance
            and not self.reservation_id.reservation_line.filtered(
                lambda line: not line.date_check_out
            )
        ):
            if self.reservation_id.balance > 0:
                payment = self.reservation_id.action_payment_create(
                    "outbound",
                    "supplier",
                    self.reservation_id.partner_id.with_company(
                        self.reservation_id.company_id
                    ).property_account_payable_id,
                )
            else:
                payment = self.reservation_id.action_payment_create(
                    "inbound",
                    "customer",
                    self.reservation_id.partner_id.with_company(
                        self.reservation_id.company_id
                    ).property_account_receivable_id,
                )
            self.reservation_id.payment_ids += payment

    @api.onchange("is_all")
    def _onchange_all(self):
        """Change all"""
        self.reservation_line_ids = False if self.is_all else self.reservation_line_ids
