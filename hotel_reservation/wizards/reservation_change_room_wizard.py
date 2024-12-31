from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ReservationRoomChangeWizard(models.TransientModel):
    _name = "reservation.room.change.wizard"
    _description = "Reservation Room Change Wizard"

    reservation_id = fields.Many2one("hotel.reservation", string="Reservation")
    reservation_line_id = fields.Many2one(
        "hotel.reservation.line", string="Reservation Line"
    )
    change_date = fields.Datetime(string="Change Date")
    old_room_id = fields.Many2one("hotel.room", string="Old Room")
    room_id = fields.Many2one("hotel.room", string="Room")
    rooms_available_ids = fields.Many2many(
        "hotel.room",
        "hotel_reservation_change_room_rel",
        compute="_compute_rooms_available",
        store=1,
    )
    insurance = fields.Float(string="Insurance")
    old_room_insurance = fields.Float(
        string="Old room Insurance", related="old_room_id.insurance", store=1
    )
    old_room_price = fields.Float(
        string="Old room Price", related="reservation_line_id.total_room_rate", store=1
    )
    discount_type = fields.Selection(
        string="Discount Type",
        selection=[
            ("no_discount", "No Discount"),
            ("percentage", "Percentage"),
            ("amount", "amount"),
        ],
        default="no_discount",
    )
    discount = fields.Float(
        string="Discount",
    )
    rent = fields.Selection(related="reservation_id.rent", store=1)
    origin_rent = fields.Selection(
        string="Origin Rent Type",
        selection=[("daily", "Daily"), ("monthly", "Monthly"), ("hours", "Hours")],
    )
    display_insurance = fields.Boolean(
        string="Display Insurance",
        compute="_compute_display_insurance_discount",
        store=1,
    )
    display_discount = fields.Boolean(
        string="Display Discount",
        compute="_compute_display_insurance_discount",
        store=1,
    )
    is_change_rent = fields.Boolean(string="Change rent")
    is_minimum_price = fields.Boolean(string="Minimum Prices")
    is_other_price = fields.Boolean(string="Other Price")
    other_price = fields.Float(string="Price")

    @api.onchange("is_minimum_price")
    def _onchange_is_minimum_price(self):
        if not self.is_minimum_price:
            self.other_price = 0
        else:
            self.is_other_price = False

    @api.onchange("is_other_price")
    def _onchange_is_other_price(self):
        if not self.is_other_price:
            self.other_price = 0
        else:
            self.is_minimum_price = False

    @api.constrains("is_other_price")
    def _check_other_price(self):
        for history in self:
            if history.is_other_price:
                if not history.other_price:
                    raise ValidationError(_("The Price must be more than 0"))
                rent = history.origin_rent if history.origin_rent else history.rent
                price = self.get_room_price(rent, self.room_id)
                if price >= history.other_price:
                    raise ValidationError(
                        _("Other price must be greater than Room Price %s") % str(price)
                    )

    @api.constrains("is_minimum_price")
    def _check_minimum_price(self):
        for history in self:
            if history.is_minimum_price:
                if not history.other_price:
                    raise ValidationError(_("Minimum Price must be more than 0"))
                rent = history.origin_rent if history.origin_rent else history.rent
                room_minimum_price = (
                    history.reservation_line_id.get_minimum_price_by_rent(
                        rent, history.room_id
                    )
                )
                if room_minimum_price > history.other_price:
                    raise ValidationError(
                        _(
                            "Minimum Price must be equal or greater than Room Minimum Price %s"
                        )
                        % room_minimum_price
                    )

    @api.onchange("origin_rent")
    def _onchange_origin_rent(self):
        """Change origin rent"""
        if self.origin_rent and self.rent:
            self.is_change_rent = True if self.origin_rent != self.rent else False

    @api.onchange("room_id")
    def _onchange_room(self):
        self.insurance = (
            self.room_id.insurance
            if not self.reservation_id.insurance
            and self.room_id.insurance
            and not self.insurance
            else 0
        )

    @api.onchange("discount_type")
    def _onchange_discount_type(self):
        """Clear the discount."""
        if self.discount_type:
            self.discount = 0

    def get_room_price(self, rent, room):
        """Get room price"""
        if rent == "daily":
            price_unit = room.list_price
        elif rent == "monthly":
            price_unit = room.monthly_price
        else:
            price_unit = room.hourly_price

        return price_unit

    @api.constrains("discount_type")
    def _check_discount_type(self):
        """Check percentage and amount."""
        for reservation_change_room in self:
            if (
                reservation_change_room.discount_type != "no_discount"
                and not reservation_change_room.discount
            ):
                if reservation_change_room.discount_type != "percentage":
                    raise ValidationError(_("You should add discount percentage"))
                else:
                    raise ValidationError(_("You should add discount amount"))

    @api.depends("room_id")
    def _compute_display_insurance_discount(self):
        for wizard in self:
            wizard.display_insurance = wizard.display_discount = False
            if (
                wizard.reservation_id.insurance
                and wizard.room_id.insurance > wizard.old_room_insurance
            ):
                wizard.display_insurance = True
            price_unit = wizard.get_room_price(wizard.rent, wizard.room_id)
            if price_unit > wizard.old_room_price:
                wizard.display_discount = True

    @api.depends(
        "reservation_id.checkout",
        "reservation_id",
        "reservation_line_id.room_id",
        "change_date",
        "reservation_id.is_vip",
    )
    def _compute_rooms_available(self):
        """Get Available rooms"""
        for reservation_room in self:
            reservation_room.rooms_available_ids = False
            domain_suite = [
                ("room_categ_id.is_vip", "=", False),
                ("company_id", "=", reservation_room.reservation_id.company_id.id),
            ]
            if reservation_room.reservation_id.is_vip:
                domain_suite = [
                    ("room_categ_id.is_vip", "=", True),
                    ("company_id", "=", reservation_room.reservation_id.company_id.id),
                ]
            date_end_reservation = (
                reservation_room.reservation_id.checkout
                if not reservation_room.reservation_line_id.date_extension
                else reservation_room.reservation_line_id.date_extension
            )
            # get availble rooms by dates and capacity
            # TODO check room capacity
            if date_end_reservation and reservation_room.change_date:
                available_rooms = (
                    reservation_room.env["hotel.room"]
                    .search(
                        [
                            ("is_withheld", "=", False),
                            (
                                "id",
                                "not in",
                                reservation_room.reservation_id.reservation_line.mapped(
                                    "room_id"
                                ).ids,
                            ),
                        ]
                        + domain_suite
                    )
                    .filtered(
                        lambda room: not room.get_status_room_dates(
                            reservation_room.reservation_id,
                            reservation_room.change_date,
                            date_end_reservation,
                        )
                        and (
                            (
                                reservation_room.reservation_id.reservation_type
                                == "individual"
                                # and room.capacity
                                # >= (
                                #     reservation_room.reservation_id.adults
                                #     + reservation_room.reservation_id.children
                                # )
                            )
                            or (
                                reservation_room.reservation_id.reservation_type
                                == "collective"
                                # and room.capacity
                                # >= (
                                #     reservation_room.reservation_line_id.adults
                                #     + reservation_room.reservation_line_id.children
                                # )
                            )
                        )
                    )
                )
                if available_rooms:
                    reservation_room.rooms_available_ids = available_rooms.ids

    def create_room_reservation_line(self, checkin, checkout):
        """Create reservation line in room."""
        self.env["hotel.room.reservation.line"].create(
            {
                "room_id": self.room_id.id,
                "check_in": checkin,
                "check_out": checkout,
                "state": "assigned",
                "reservation_id": self.reservation_id.id,
                "reservation_line_id": self.reservation_line_id.id,
            }
        )
        self.env["folio.room.line"].create(
            {
                "room_id": self.room_id.id,
                "check_in": checkin,
                "check_out": checkout,
                "folio_id": self.reservation_id.folio_id.id,
                "reservation_line_id": self.reservation_line_id.id,
            }
        )

    # flake8: noqa: C901
    def action_change_room(self):
        """Change Room."""
        # update value of insurance and discount change room
        old_final_cost = self.reservation_id.final_cost
        self.reservation_id.insurance_change_room = self.reservation_id.insurance
        self.reservation_line_id.discount_change_room = 0
        # get state of folio and invoice
        folio_state = self.reservation_id.folio_id.state
        invoice_state = (
            self.reservation_id.folio_id.hotel_invoice_id.state
            if self.reservation_id.folio_id.hotel_invoice_id
            else False
        )
        # when choose different rent recalculate rate
        if self.origin_rent != self.rent:
            old_rent = self.reservation_id.rent
            self.reservation_id.rent = self.origin_rent
            self.reservation_id._onchange_checkin_checkout()
            self.reservation_id._compute_total_room_rate()
            self.reservation_id.message_post(
                body=_("Change Room leads to change rent type  from {} to {}").format(
                    old_rent,
                    self.origin_rent,
                )
            )

        old_room_id = self.reservation_line_id.room_id
        old_minimum_price = self.reservation_line_id.other_price
        # get date start reservation room
        reservation_date = (
            self.reservation_id.checkin
            if not self.reservation_line_id.change_date
            else self.reservation_line_id.change_date
        )
        # get history without no calculated line
        history_rooms = self.reservation_id.history_room_ids.filtered(
            lambda history: not history.is_no_calculated
            and history.reservation_line_id == self.reservation_line_id
        )
        payments = (
            self.env["account.payment"]
            .search([])
            .filtered(
                lambda pay: self.reservation_id.folio_id.hotel_invoice_id.id
                in pay.reconciled_invoice_ids.ids
            )
        )

        for history_room in history_rooms:
            # get last old room
            change_date = (
                self.change_date
                if self.reservation_id.rent == "hours"
                else self.change_date.date()
            )
            history_change_date = (
                history_room.change_date
                if self.reservation_id.rent == "hours"
                else history_room.change_date.date()
            )
            if change_date > history_change_date:
                old_room_id = history_room.room_id
                old_minimum_price = history_room.other_price
            # change date mess than first date of change
            if change_date <= history_change_date:

                # remove room from folio and invoice
                # get folio line
                room_line = self.reservation_id.folio_id.room_line_ids.filtered(
                    lambda line: line.product_id == history_room.room_id.product_id
                )
                # set folio and invoice to draft
                self.reservation_id.set_folio_draft()
                # delete room from folio and invoice
                if room_line:
                    if room_line.invoice_lines:
                        room_line.invoice_lines.filtered(
                            lambda inv_line: inv_line.product_id.id
                            == room_line.product_id.id
                        ).with_context(check_move_validity=False).unlink()
                    room_line[0].unlink()
                # ths line of history is no calculated
                history_room.is_no_calculated = True
                # get reservation start date
                reservation_date = history_room.reservation_date
                # we change the room with insurance with other who
                # hasn't insurance in the same day. remove insurance
                if self.reservation_id.insurance > 0:
                    self.reservation_id.insurance_change_room -= history_room.insurance
                    self.reservation_id.insurance -= history_room.insurance
        # Create new history line from change room
        last_history = self.env["reservation.room.change.history"].create(
            {
                "reservation_id": self.reservation_id.id,
                "reservation_line_id": self.reservation_line_id.id,
                "change_date": self.change_date,
                "old_room_id": old_room_id.id,
                "room_id": self.room_id.id,
                "reservation_date": reservation_date,
                "discount": self.discount,
                "insurance": self.insurance,
                "discount_type": self.discount_type,
                "old_other_price": old_minimum_price,
                "other_price": self.other_price,
            }
        )
        # remove room reservations
        if (
            last_history.reservation_date.date() == last_history.change_date.date()
            and self.reservation_id.rent in ["daily", "monthly"]
        ):
            room_line = old_room_id.room_line_ids.filtered(
                lambda line: line.check_in.date()
                == last_history.reservation_date.date()
            )
            if room_line:
                room_line[0].unlink()
            room_reservation_line = old_room_id.room_reservation_line_ids.filtered(
                lambda room_reservation: room_reservation.check_in.date()
                == last_history.reservation_date.date()
            )
            if room_reservation_line:
                room_reservation_line[0].unlink()
        self.reservation_line_id.change_date = self.change_date
        # recalculate insurance
        self.reservation_id.insurance_change_room += self.insurance

        self.reservation_id.insurance += self.insurance
        if self.get_room_price(self.rent, self.room_id) != self.get_room_price(
            self.rent, self.old_room_id
        ):
            # show discount when price of old and new room is diffrents
            self.reservation_id._compute_total_room_rate()

        final_cost = self.reservation_id.final_cost
        if not (final_cost < old_final_cost and payments):
            self.reservation_id.set_folio_draft()
        for history in self.reservation_id.history_room_ids.filtered(
            lambda history: not history.is_no_calculated
            and history.reservation_line_id == self.reservation_line_id
        ):
            # get folio line and duration and checkout

            room_line = self.reservation_id.folio_id.room_line_ids.filtered(
                lambda line: line.product_id == history.old_room_id.product_id
            )
            duration = self.reservation_id.get_duration_change_room(
                history.reservation_date, history.change_date, self.origin_rent
            )
            # get histories created before current history to get discount
            before_histories = self.reservation_id.history_room_ids.filtered(
                lambda before_history: not before_history.is_no_calculated
                and before_history.id < history.id
                and before_history.reservation_line_id == self.reservation_line_id
            )
            if (
                history.reservation_date.date() == history.change_date.date()
                and self.reservation_id.rent in ["monthly", "daily"]
            ):
                duration = 0
            checkout = history.change_date + relativedelta(days=int(-1))
            if checkout.date() < self.reservation_id.checkin.date():
                checkout = self.reservation_id.checkin
            # if change the room with insurance with other
            # who hasn't insurance. set insurance to 0
            if (
                not before_histories
                and self.reservation_id.insurance
                and not self.insurance
                and history.reservation_date.date() == history.change_date.date()
            ):
                self.reservation_id.insurance_change_room = (
                    self.reservation_id.insurance
                ) = 0
            # we change the room with insurance with other who
            # hasn't insurance in the same day. remove insurance
            if (
                self.change_date.date() == history.change_date.date()
                and self.reservation_id.insurance > 0
                and last_history != history
            ):
                self.reservation_id.insurance_change_room -= history.insurance
                self.reservation_id.insurance -= history.insurance
            if (
                before_histories
                and duration
                and before_histories[-1].discount_type != "no_discount"
            ):
                old_room_price_unit = self.reservation_id.get_price(
                    history.old_other_price,
                    self.reservation_id.rent,
                    history.old_room_id,
                    self.reservation_id.company_id,
                    history.reservation_date,
                    checkout,
                    duration,
                )
                # calculate discount of old rooms
                self.reservation_line_id.discount_change_room += (
                    before_histories[-1].discount
                    if before_histories[-1].discount_type != "percentage"
                    else (
                        (old_room_price_unit * duration) * before_histories[-1].discount
                    )
                    / 100
                )
            if final_cost < old_final_cost and payments:
                room_line.write(
                    {
                        "checkout_date": checkout,
                        "product_uom_qty": int(duration),
                    }
                )
                self.reservation_id.update_room_reservation_line(
                    room_line[0].reservation_line_id, history.old_room_id, checkout
                )
                if (
                    self.reservation_id.folio_id
                    and self.reservation_id.folio_id.hotel_invoice_id
                ):
                    self.reservation_id.folio_id.hotel_invoice_id.is_no_refund = False
            else:
                # update folio and invoice line
                if not room_line and history.reservation_line_id:
                    self.reservation_id.update_room_reservation_line(
                        history.reservation_line_id, history.old_room_id, checkout
                    )
                if room_line:
                    self.reservation_id.update_folio_invoice(
                        room_line[0],
                        history.old_room_id,
                        checkout,
                        duration,
                        self.is_change_rent,
                    )
        # get checkin and duration and checkout and price unit
        checkout = (
            self.reservation_line_id.date_extension
            if self.reservation_line_id.date_extension
            else self.reservation_id.checkout
        )
        if (
            self.reservation_line_id.date_termination
            and self.reservation_id.is_returnable
        ):
            checkout = self.reservation_line_id.date_termination
        checkin = self.change_date
        duration = self.reservation_id.get_duration_change_room(
            checkin, checkout, self.reservation_id.rent
        )
        price_unit = self.reservation_id.get_price(
            self.other_price,
            self.reservation_id.rent,
            self.room_id,
            self.reservation_id.company_id,
            checkin,
            checkout,
            duration,
        )
        # calculate discount of new rooms
        if self.discount_type != "no_discount":
            self.reservation_line_id.discount_change_room += (
                self.discount
                if self.discount_type != "percentage"
                else ((price_unit * duration) * self.discount) / 100
            )
        # don't change invoice if the new room is cheap than the ols room
        if not (final_cost < old_final_cost and payments):
            # create folio and invoice line for new rooms
            self.reservation_id.create_folio_line(
                self.reservation_id.folio_id,
                self.reservation_line_id,
                self.room_id,
                checkin,
                checkout,
                duration,
                price_unit,
                self.reservation_id.discount_change_room,
                self.reservation_id.insurance,
            )
            # post folio and invoice
            self.reservation_id.post_folio_invoice(folio_state, invoice_state, payments)
        # create reservation line in room
        self.create_room_reservation_line(checkin, checkout)
        if (
            datetime.today().date() == self.change_date.date() and self.rent != "hours"
        ) or (datetime.today() == self.change_date and self.rent == "hours"):
            # change state of old room and new room
            self.reservation_line_id.room_id.status = "available"
            if self.reservation_line_id.line_id.date_check_in:
                self.reservation_line_id.room_id.is_clean = False
            self.room_id.status = "occupied"
            if self.reservation_id.reservation_type == "individual":
                self.reservation_id.partner_id.last_room_id = self.room_id.id
            else:
                partner = (
                    self.reservation_line_id.partner_id
                    if self.reservation_line_id.tenant == "person"
                    else self.reservation_line_id.partner_company_id
                )
                partner.last_room_id = self.room_id.id
            self.reservation_line_id.room_id = self.room_id.id
            self.reservation_line_id.other_price = self.other_price

    @api.constrains("change_date")
    def _check_change_date(self):
        """Check change date."""
        for reservation_change in self:
            if reservation_change.change_date:
                checkout = (
                    reservation_change.reservation_id.checkout
                    if not reservation_change.reservation_line_id.date_extension
                    else reservation_change.reservation_line_id.date_extension
                )
                if reservation_change.reservation_line_id.date_termination:
                    checkout = reservation_change.reservation_line_id.date_termination
                if reservation_change.reservation_id.rent != "hours":
                    checkout = checkout.date()

                change_date = (
                    reservation_change.change_date
                    if reservation_change.reservation_id.rent == "hours"
                    else reservation_change.change_date.date()
                )
                checkin = (
                    reservation_change.reservation_id.checkin
                    if reservation_change.reservation_id.rent == "hours"
                    else reservation_change.reservation_id.checkin.date()
                )
                if change_date < checkin:
                    raise ValidationError(
                        _(
                            "Change Date should be greater or equal to  date start reservation"
                        )
                    )
                if reservation_change.change_date.date() < datetime.today().date():
                    raise ValidationError(
                        _("Change Date should be greater or equal to today")
                    )
                if change_date > checkout:
                    raise ValidationError(
                        _("Change Date should be less than reservation end date")
                    )
