import math
from datetime import datetime, time, timedelta
import pytz
from dateutil.relativedelta import relativedelta
from ummalqura.hijri_date import HijriDate
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.osv import expression
import logging
# service_line_ids
# folio_id
# balance
# is_hospitality
# action_check_in_check_out
_logger = logging.getLogger(__name__)
class HotelReservation(models.Model):
    _name = "hotel.reservation"
    _rec_name = "reservation_no"
    _description = "Reservation"
    _order = "reservation_no desc"
    _inherit = ["mail.thread", "mail.activity.mixin", "rating.mixin"]



    related_invoice_ids = fields.One2many(
        comodel_name='account.move', # Assuming 'account.move' is the model for invoices
        compute='_compute_related_invoices',
    )

    @api.depends('folio_id.order_id') # Adjust depending on your specific relationship
    def _compute_related_invoices(self):
        for folio in self:
            folio.related_invoice_ids = folio.order_id.mapped('invoice_ids')

    total_inbound_payments = fields.Float(
        string="Total Inbound Payments", compute="_compute_payment_totals"
    )
    total_inbound_insurance = fields.Float(
        string="Total Inbound Insurance", compute="_compute_payment_totals"
    )
    total_outbound_payments = fields.Float(
        string="Total Outbound Payments", compute="_compute_payment_totals"
    )
    total_outbound_insurance = fields.Float(
        string="Total Outbound insurance", compute="_compute_payment_totals"
    )


    amount_due = fields.Float(
        string="Amount Due",
        compute="_compute_amount_due"
    )
    @api.depends('total_inbound_payments', 'total_inbound_insurance', 'total_outbound_payments', 'total_outbound_insurance')
    def _compute_amount_due(self):
        # inisilize amount_due
        
        self.amount_due = 0.0
        self.amount_due = (self.total_inbound_payments + self.total_inbound_insurance) - (self.total_outbound_payments + self.total_outbound_insurance)
        

    
    # @api.depends('payment_ids.amount', 'payment_ids.payment_type')
    # def _compute_payment_totals(self):
    #     for reservation in self:
    #         inbound_total = 0.0
    #         outbound_total = 0.0
    #         # Ensure every record gets a value, even if it's zero
    #         for payment in reservation.payment_ids.filtered(lambda p: p.state == 'posted'):
    #             if payment.payment_type == 'inbound':
    #                 inbound_total += payment.amount
    #             elif payment.payment_type == 'outbound':
    #                 outbound_total += payment.amount
    #         # Assign computed values
    #         reservation.total_inbound_payments = inbound_total
    #         reservation.total_outbound_payments = outbound_total
            
            
    def _compute_folio_count(self):
        for res in self:
            res.update({"no_of_folio": len(res.folio_id.ids)})

    
    reservation_no = fields.Char("Reservation No", readonly=True)
    date_order = fields.Datetime(
        "Date Ordered",
        readonly=True,
        required=True,
        index=True,
        default=lambda self: fields.Datetime.now(),
    )
    return_insurance = fields.Boolean(string="Return Insurance", required=True, default=False)
    return_insurance_amount = fields.Float(string="Return Insurance Amount")
    @api.onchange('return_insurance')
    def _onchange_return_insurance(self):
        if self.return_insurance:
            self.return_insurance_amount = self.insurance
            
    company_id = fields.Many2one(
        "res.company",
        "Hotel",
        readonly=True,
        index=True,
        required=True,
        states={"draft": [("readonly", False)]},
        default=lambda self: self.env.company,
    )
    partner_id = fields.Many2one(
        "res.partner",
        "Guest Name",
        readonly=True,
        index=True,
        required=True,
        domain="[('is_guest', '=', True)]",
        states={"draft": [("readonly", False)]},
    )
    def check_partner_required_fields(self, partner):
        """
        Check if all required fields for a guest are filled.
        @param partner: The partner (guest) record.
        """
        required_fields = ['name', 'guest_type', 'identification_id', 'birthday', 'gender', 'nationality_id', 'mobile', 'country_id']  # Define required fields
        missing_fields = [
            field for field in required_fields
            if not getattr(partner, field, False)
        ]
        if missing_fields:
            raise ValidationError(
                'Please fill in all required fields for the guest: %s.' % ', '.join(missing_fields)
            )

    
    partner_invoice_id = fields.Many2one(
        "res.partner",
        "Invoice Address",
        readonly=True,
        states={"draft": [("readonly", False)]},
        help="Invoice address for " "current reservation.",
    )
    partner_order_id = fields.Many2one(
        "res.partner",
        "Ordering Contact",
        readonly=True,
        states={"draft": [("readonly", False)]},
        help="The name and address of the "
        "contact that requested the order "
        "or quotation.",
    )
    partner_shipping_id = fields.Many2one(
        "res.partner",
        "Delivery Address",
        readonly=True,
        states={"draft": [("readonly", False)]},
        help="Delivery address" "for current reservation. ",
    )
    checkin = fields.Datetime(
        "Expected-Date-Arrival",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        tracking=1,
        default=lambda self: fields.Datetime.now(),
    )
    checkout = fields.Datetime(
        "Expected-Date-Departure",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        tracking=1,
    )
    adults = fields.Integer(
        "Number Adults",
        readonly=True,
        states={"draft": [("readonly", False)]},
        help="List of adults there in guest list. ",
    )
    children = fields.Integer(
        "Number Children",
        readonly=True,
        states={"draft": [("readonly", False)]},
        help="Number of children there in guest list.",
    )
    reservation_line = fields.One2many(
        "hotel.reservation.line",
        "line_id",
        string="Reservation Line",
        help="Hotel room reservation details.",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirm", "Pre-booking"),
            ("done", "Done"),
            ("finish", "Finished"),
            ("cancel", "Cancel"),
        ],
        "State",
        readonly=True,
        default="draft",
        tracking=1,
    )
    folio_id = fields.Many2many(
        "hotel.folio",
        "hotel_folio_reservation_rel",
        "order_id",
        "invoice_id",
        string="Folio",
        copy=False,
    )
    hotel_invoice_id = fields.Many2one(related="folio_id.hotel_invoice_id", store=1)
    
    related_invoice_ids = fields.Many2many('account.move', compute='_compute_related_invoices', string='Related Invoices')

    @api.depends('folio_id.invoice_ids')
    def _compute_related_invoices(self):
        for record in self:
            # Directly linking the invoices associated with the folio of this reservation
            record.related_invoice_ids = record.folio_id.invoice_ids
    no_of_folio = fields.Integer("No. Folio", compute="_compute_folio_count")
    
    source_id = fields.Many2one(
        "hotel.reservation.source",
        string="Source Reservation",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    rent = fields.Selection(
        string="Rent Type",
        selection=[("daily", "Daily"), ("monthly", "Monthly"), ("hours", "Hours")],
        default="daily",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    source_number = fields.Char(
        string="Reservation source number",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    
    duration = fields.Integer(
        string="Duration",
        readonly=True,
        states={"draft": [("readonly", False)]},
        default=1,
    )
    reason_id = fields.Many2one(
        "reservation.visit.reason",
        string="Visit Reason",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    note = fields.Text(
        string="Notes",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    reservation_type = fields.Selection(
        string="Reservation Type",
        selection=[("individual", "Individual"), ("collective", "Collective")],
        default="individual",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    room_rate = fields.Float(
        string="Rooms Rate", compute="_compute_total_room_rate", store=1
    )
    total_room_rate = fields.Float(
        string="Untaxed Total Rate", compute="_compute_total_room_rate", store=1
    )
    children_ids = fields.Many2many(
        "res.partner",
        "reservation_related_children_rel",
        string="Children",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    adults_ids = fields.Many2many(
        "res.partner",
        "reservation_related_adults_rel",
        string="Adults",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    discount_type = fields.Selection(
        string="Discount Type",
        selection=[
            ("no_discount", "No Discount"),
            ("percentage", "Percentage"),
            ("amount", "amount"),
        ],
        default="no_discount",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    discount_percentage = fields.Float(
        string="Percentage",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    discount = fields.Float(
        string="Discount",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    insurance = fields.Float(
        string="Insurance",
        readonly=True,
        states={"draft": [("readonly", False)], "confirm": [("readonly", False)]},
    )
    insurance_change_room = fields.Float(string="Insurance Change Room")
    discount_change_room = fields.Float(
        string="Discount Change Room", compute="_compute_total_room_rate", store=1
    )
    taxes_amount = fields.Float(
        string="Taxes ", compute="_compute_total_room_rate", store=1
    )
    taxed_total_rate = fields.Float(
        string="Taxed Total Rate", compute="_compute_total_room_rate", store=1
    )
    total_cost = fields.Float(
        string="Total Cost", compute="_compute_total_room_rate", store=1
    )
    final_cost = fields.Float(
        string="Final cost",
        compute="_compute_total_room_rate",
        store=1,
        tracking=1,
    )
    payments_count = fields.Float(
        string="Payments", compute="_compute_payments", store=1
    )
    payment_totals = fields.Text(
        string="Payment Totals", compute="_compute_payment_totals"
    )
    balance = fields.Float(string="Balance", compute="_compute_payments", store=1)
    is_send_shomoos = fields.Boolean(string="Send to Shomoos Service")
    is_send_tourism = fields.Boolean(string="Send to Tourism Platform Service")
    service_amount = fields.Float(
        string="Services", related="folio_id.service_amount", store=1
    )
    service_tax = fields.Float(
        string="Services Tax", related="folio_id.service_tax", store=1
    )
    is_returnable = fields.Boolean(
        string="Returnable",
        readonly=True,
        states={"draft": [("readonly", False)]},
        default=True,
    )
    returnable_percentage = fields.Float(
        string="Percentage ",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    returnable_amount = fields.Float(
        string="Returned Amount ",
        compute="_compute_total_room_rate",
        store=1,
    )
    is_returnable_reservation = fields.Boolean(
        string="Returnable Reservation", copy=False
    )
    date_check_in = fields.Datetime(string="Check in", readonly=1)
    date_check_out = fields.Datetime("Check Out", readonly=1)
    duration_check = fields.Integer(
        string="Check Duration", compute="_compute_check_duration", store=1
    )
    display_button_terminate_reservation = fields.Boolean(
        string="Display button terminate reservation",
        compute="_compute_display_button_reservation",
    )
    display_button_check_in_reservation = fields.Boolean(
        string="Display button check in reservation",
        compute="_compute_display_button_reservation",
    )
    display_button_check_out_reservation = fields.Boolean(
        string="Display button check out reservation",
        compute="_compute_display_button_reservation",
    )
    display_button_extend_reservation = fields.Boolean(
        string="Display button extend reservation",
        compute="_compute_display_button_reservation",
    )
    display_button_cancel = fields.Boolean(
        string="Display button cancel reservation",
        compute="_compute_display_button_reservation",
    )
    display_button_returned_reservation = fields.Boolean(
        string="Display button returned reservation",
        compute="_compute_display_button_reservation",
    )
    is_vip = fields.Boolean(
        string="VIPS",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    history_room_ids = fields.One2many(
        "reservation.room.change.history", "reservation_id", string="History Rooms"
    )
    reason_cancel = fields.Text(string="Cancel Reason", readonly=1)
    rated_partner_id = fields.Many2one("res.partner", string="Rated Partner")
    is_checked_in = fields.Boolean(
        string="Is Checked In", compute="_compute_is_checked_in", store=True
    )
    is_checked_out = fields.Boolean(
        string="Is Checked Out", compute="_compute_is_checked_out", store=True
    )
    date_termination = fields.Datetime(string="Termination Date", readonly=1)
    mobile = fields.Char(related="partner_id.mobile", store=1)
    identification_id = fields.Char(related="partner_id.identification_id", store=1)
    visa_number = fields.Char(related="partner_id.visa_number", store=1)
    card_number = fields.Char(related="partner_id.card_number", store=1)
    residence_number = fields.Char(related="partner_id.residence_number", store=1)
    passport_id = fields.Char(related="partner_id.passport_id", store=1)
    is_hospitality = fields.Boolean(
        string="Hospitality",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    payment_ids = fields.One2many(
        "account.payment", "reservation_id", string="Payments", index=True
    )
    rooms = fields.Char(string="Rooms", compute="_compute_rooms")
    taxes_info = fields.Text(string="Taxes details")

    def _format_date(self, naive_dt):
        """Convert datetime from utc to tz"""
        naive = datetime.strptime(naive_dt[:19], "%Y-%m-%d %H:%M:%S")
        tz_name = self.env.user.tz
        tz = pytz.timezone(tz_name) if tz_name else pytz.utc
        ran = pytz.utc.localize(naive).astimezone(tz)
        date = datetime.strptime(str(ran)[:19], "%Y-%m-%d %H:%M:%S")
        return date

    def get_hour_minute_float(self, float_val):
        """Get hour and minute from float"""
        factor = float_val < 0 and -1 or 1
        val = abs(float_val)
        hour, minute = (factor * int(math.floor(val)), int(round((val % 1) * 60)))
        if minute == 60:
            hour = hour + 1
            minute = 0
        return hour, minute

    def _compute_rooms(self):
        """Get rooms numbers"""
        for reservation in self:
            rooms = set(
                reservation.reservation_line.mapped("room_id")
                + reservation.history_room_ids.filtered(
                    lambda history: not history.is_no_calculated
                    and history.reservation_date.date() != history.change_date.date()
                ).mapped("room_id")
                + reservation.history_room_ids.filtered(
                    lambda history: not history.is_no_calculated
                    and history.reservation_date.date() != history.change_date.date()
                ).mapped("old_room_id")
            )
            reservation.rooms = ", ".join(room.name for room in rooms)


    @api.depends("date_check_in", "reservation_line.date_check_in")
    def _compute_is_checked_in(self):
        """Calculate Check Duration."""
        for reservation in self:
            reservation.is_checked_in = False
            if (
                reservation.reservation_type == "individual"
                and reservation.date_check_in
            ) or (
                reservation.reservation_type == "collective"
                and all(reservation.mapped("reservation_line.date_check_in"))
            ):
                reservation.is_checked_in = True

    @api.depends("date_check_out", "reservation_line.date_check_out")
    def _compute_is_checked_out(self):
        """Calculate Check Duration."""
        for reservation in self:
            reservation.is_checked_out = False
            if (
                reservation.reservation_type == "individual"
                and reservation.date_check_out
            ) or (
                reservation.reservation_type == "collective"
                and all(reservation.mapped("reservation_line.date_check_out"))
            ):
                reservation.is_checked_out = True

    def unlink(self):
        """
        Overrides orm unlink method.
        @param self: The object pointer
        @return: True/False.
        """
        lines_of_moves_to_post = self.filtered(
            lambda reserv_rec: reserv_rec.state != "draft"
        )
        if lines_of_moves_to_post:
            raise ValidationError(
                _("Sorry, you can only delete the reservation when it's draft!")
            )
        quick_reservation_ids = self.env["quick.room.reservation"].search(
            [("reservation_id", "=", self.id)]
        )
        quick_reservation_ids.unlink()
        return super(HotelReservation, self).unlink()

    def copy(self):
        ctx = dict(self._context) or {}
        ctx.update({"duplicate": True})
        return super(HotelReservation, self.with_context(ctx)).copy()

    @api.constrains("reservation_line", "adults", "children")
    def _check_reservation_rooms(self):
        """
        This method is used to validate the reservation_line.
        -----------------------------------------------------
        @param self: object pointer
        @return: raise a warning depending on the validation
        """
        dict(self._context) or {}
        for reservation in self:
            # TODO check room capacity

            # if not ctx.get("duplicate"):
            #     if reservation.reservation_line.mapped("room_id") and (
            #         reservation.adults + reservation.children
            #     ) > sum(reservation.reservation_line.mapped("room_id.capacity")):
            #         raise ValidationError(
            #             _(
            #                 "Room Capacity Exceeded \n"
            #                 " Please Select Rooms According to"
            #                 " Members Accomodation."
            #             )
            #         )
            if (
                reservation.reservation_type == "individual"
                and len(reservation.adults_ids) != reservation.adults
            ):
                raise ValidationError(
                    _(
                        "The number of adults must correspond to the number of selected adults."
                    )
                )

    @api.constrains("checkin", "checkout")
    def check_in_out_dates(self):
        """
        When date_order is less then check-in date or
        Checkout date should be greater than the check-in date.
        """
        if self.checkout and self.checkin:
            if self.checkin.date() < self.date_order.date():
                raise ValidationError(
                    _(
                        """Check-in date should be greater than """
                        """the current date."""
                    )
                )
            if self.checkout <= self.checkin:
                raise ValidationError(
                    _("""Check-out date should be greater """ """than Check-in date.""")
                )

    @api.onchange("reservation_line")
    def _onchange_reservation_line(self):
        for reservation in self:
            if (
                reservation.reservation_type == "individual"
                and len(reservation.reservation_line) > 1
            ):
                raise ValidationError(
                    _("You cannot add more than one room for individual reservation .")
                )

    @api.onchange("discount_type")
    def _onchange_discount_type(self):
        """Change discount value based on hospitality."""
        if self.discount_type:
            self.discount_percentage = 0
            self.discount = 0
            # change discount based on type Hospitality
            if self.is_hospitality:
                reservation_hospitality = self.env[
                    "hotel.reservation.hospitality"
                ].search([("company_id", "=", self.company_id.id)], limit=1)
                if reservation_hospitality.discount_type == "amount":
                    self.discount = reservation_hospitality.discount
                else:
                    self.discount_percentage = reservation_hospitality.discount

    @api.onchange("is_hospitality")
    def _onchange_hospitality(self):
        """Change discount value when check hospitality."""
        # change discount type based on type Hospitality
        if self.is_hospitality:
            reservation_hospitality = self.env["hotel.reservation.hospitality"].search(
                [("company_id", "=", self.company_id.id)], limit=1
            )
            if reservation_hospitality:
                self.discount_type = reservation_hospitality.discount_type
        else:
            self.discount_type = "no_discount"
            self.discount_percentage = 0
            self.discount = 0

    @api.onchange("is_returnable")
    def _onchange_is_returnable(self):
        """Clear returnable percentage."""
        if not self.is_returnable:
            self.returnable_percentage = 0

    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        """
        When you change partner_id it will update the partner_invoice_id,
        partner_shipping_id  of the hotel reservation as well
        ---------------------------------------------------------------------
        @param self: object pointer
        """
        if not self.partner_id:
            self.update(
                {
                    "partner_invoice_id": False,
                    "partner_shipping_id": False,
                    "partner_order_id": False,
                }
            )
        else:
            addr = self.partner_id.address_get(["delivery", "invoice", "contact"])
            self.update(
                {
                    "partner_invoice_id": addr["invoice"],
                    "partner_shipping_id": addr["delivery"],
                    "partner_order_id": addr["contact"],
                }
            )

    def _create_quick_reservation(self):
        """Create quick reservation when create new reservation
        or add new line in reservation created."""
        for line in self.reservation_line:
            domain = [
                ("reservation_id", "=", self.id),
                ("room_id", "=", line.room_id.id),
            ]
            # Get the right value of guest to check if quick reservation created or no.
            # Check if the thype of reservation is individual
            # to get the value of guest from individual.
            if self.reservation_type == "individual":
                domain = expression.AND(
                    [domain, [("partner_id", "=", self.partner_id.id)]]
                )
            else:
                # If the type of reservation is collective we will check if this reservation
                # for company or person to get the right value of guest.
                if line.tenant == "person":
                    domain = expression.AND(
                        [domain, [("partner_id", "=", line.partner_id.id)]]
                    )
                else:
                    domain = expression.AND(
                        [domain, [("partner_id", "=", line.partner_company_id.id)]]
                    )
            quick_reservation_ids = self.env["quick.room.reservation"].search(domain)
            if not quick_reservation_ids:
                val = {
                    "reservation_id": self.id,
                    "partner_id": self.partner_id.id,
                    "room_id": line.room_id.id,
                    "check_in": self.checkin,
                    "check_out": self.checkout,
                    "source_id": self.source_id.id,
                    "source_number": self.source_number,
                    "is_returnable": self.is_returnable,
                    "returnable_percentage": self.returnable_percentage,
                    "company_id": self.company_id.id,
                    "partner_invoice_id": self.partner_invoice_id.id,
                    "partner_order_id": self.partner_order_id.id,
                    "partner_shipping_id": self.partner_shipping_id.id,
                    "reason_id": self.reason_id.id,
                    "adults": self.adults,
                }
                if self.reservation_type == "collective":
                    if line.tenant == "person":
                        val.update({"partner_id": line.partner_id.id})
                    else:
                        val.update({"partner_id": line.partner_company_id.id})
                self.env["quick.room.reservation"].create(val)

    def create_housekeeping(self, rooms):
        for room in rooms:
            vals = {
                "reservation_id": self.id,
                "categ_id": room.room_categ_id.id,
                "type": "cleanliness",
                "clean_type": "checkout",
                "room_id": room.id,
                "company_id": self.company_id.id,
                "inspect_date_time": fields.Datetime.now(),
            }
            activity = (
                self.env["hotel.activity"]
                .sudo()
                .search([("categ_id.type", "=", "cleanliness")], limit=1)
            )
            clean_user = (
                self.env["res.users"]
                .sudo()
                .search(
                    [
                        (
                            "groups_id",
                            "=",
                            self.env.ref("hotel_housekeeping.group_clean_worker").id,
                        )
                    ],
                    limit=1,
                )
            )
            if activity and clean_user:
                clean_user = (
                    self.env["res.users"]
                    .sudo()
                    .search(
                        [
                            (
                                "groups_id",
                                "=",
                                self.env.ref(
                                    "hotel_housekeeping.group_clean_worker"
                                ).id,
                            )
                        ],
                        limit=1,
                    )
                )
                vals_activity = {
                    "activity_id": activity.id,
                    "housekeeper_id": clean_user.id,
                    "clean_start_time": fields.Datetime.now(),
                    "clean_end_time": fields.Datetime.now() + timedelta(hours=1),
                    "today_date": datetime.today().date(),
                }
                vals.update({"activity_line_ids": [(0, 0, vals_activity)]})
            housekeeping = self.env["hotel.housekeeping"].sudo().create(vals)
            housekeeping._onchange_room()

    # @api.model
    # def create(self, vals):
    #     """
    #     Overrides orm create method.
    #     @param self: The object pointer
    #     @param vals: dictionary of fields value.
    #     """
    #     reservation = super(HotelReservation, self).create(vals)
    #     if reservation:
    #         reservation.reservation_no = self.env["ir.sequence"].next_by_code(
    #             "hotel.reservation"
    #         )
    #         reservation._create_quick_reservation()
    #         if len(reservation.reservation_line):
    #             reservation.partner_id.last_room_id = reservation.reservation_line[
    #                 0
    #             ].room_id.id
    #     return reservation

    @api.model
    def create(self, vals):
        """
        Override the create method to include the check for partner required fields,
        then proceed with reservation creation.
        """
        # If partner_id is in the vals, get the partner record and check required fields
        if 'partner_id' in vals:
            partner = self.env['res.partner'].browse(vals['partner_id'])
            self.check_partner_required_fields(partner)
        
        # Proceed with creating the reservation
        reservation = super(HotelReservation, self).create(vals)
        if reservation:
            # Additional logic for setting up the reservation
            reservation.reservation_no = self.env["ir.sequence"].next_by_code(
                "hotel.reservation"
            )
            reservation._create_quick_reservation()
            if len(reservation.reservation_line):
                reservation.partner_id.last_room_id = reservation.reservation_line[
                    0
                ].room_id.id
        
        return reservation
    def write(self, vals):
        # Do not allow changing the company_id when account_move_line already exist
        reservation = super(HotelReservation, self).write(vals)
        if (
            vals.get("checkin", False)
            or vals.get("checkout", False)
            or vals.get("reservation_line", False)
        ):
            self._create_quick_reservation()
            if len(self.reservation_line):
                self.partner_id.last_room_id = self.reservation_line[0].room_id.id
        return reservation

    def check_overlap(self, date1, date2):
        delta = date2 - date1
        return {date1 + timedelta(days=i) for i in range(delta.days + 1)}

    def print_invoice(self):
        return self.env.ref("account.account_invoices_without_payment").report_action(
            self.hotel_invoice_id
        )

    def confirmed_reservation(self):
        """
        This method create a new record set for hotel room reservation line
        -------------------------------------------------------------------
        @param self: The object pointer
        @return: new record set for hotel room reservation line.
        """
        if self.checkout and self.checkin:
            checkin_datetime = fields.Datetime.from_string(self.checkin)
            checkout_datetime = fields.Datetime.from_string(self.checkout)
            checkin_date = checkin_datetime.date()
            checkout_date = checkout_datetime.date()
            checkin_time = checkin_datetime.time()

            # If check-in date is before the order date
            if checkin_date < self.date_order.date():
                raise ValidationError(_("Check-in date should be greater than the current date."))

            # If check-out is before check-in
            if checkout_datetime <= checkin_datetime:
                raise ValidationError(_("Check-out date should be greater than Check-in date."))

            # If check-in and check-out are on the same day and check-in is after 4:00 AM
            if checkin_date == checkout_date and checkin_time >= time(4, 0, 0):
                # The check-out date should be the next day
                expected_checkout_date = (checkin_datetime + timedelta(days=1)).date()
                if checkout_date != expected_checkout_date:
                    raise ValidationError(
                        _("Check-out must be on the next day after 4:00 AM check-in.")
                    )
        reservation_line_obj = self.env["hotel.room.reservation.line"]
        vals = {}
        for reservation in self:
            if not len(reservation.reservation_line):
                raise ValidationError(_("Please Select Rooms For Reservation."))
            reserv_checkin = reservation.checkin
            reserv_checkout = reservation.checkout
            room_bool = False
            # Check availability of rooms
            for reservation_line in reservation.reservation_line:
                if reservation_line.room_id.room_reservation_line_ids:
                    for (
                        reserv
                    ) in reservation_line.room_id.room_reservation_line_ids.search(
                        [
                            ("status", "in", ("confirm", "done")),
                            ("room_id", "=", reservation_line.room_id.id),
                        ]
                    ):
                        if (
                            not reserv.reservation_id.date_check_out
                            and reserv.reservation_id.reservation_type == "individual"
                        ) or (
                            not reserv.reservation_line_id.date_check_out
                            and reserv.reservation_line_id.room_id
                            == reservation_line.room_id
                            and reservation_line.line_id.reservation_type
                            == "collective"
                        ):
                            check_in = reserv.check_in
                            check_out = reserv.check_out
                            if check_in <= reserv_checkin <= check_out:
                                room_bool = True
                            if check_in <= reserv_checkout <= check_out:
                                room_bool = True
                            if (
                                reserv_checkin <= check_in
                                and reserv_checkout >= check_out
                            ):
                                room_bool = True
                            r_checkin = (reservation.checkin).date()
                            r_checkout = (reservation.checkout).date()
                            check_intm = (reserv.check_in).date()
                            check_outtm = (reserv.check_out).date()
                            range1 = [r_checkin, r_checkout]
                            range2 = [check_intm, check_outtm]
                            overlap_dates = self.check_overlap(
                                *range1
                            ) & self.check_overlap(*range2)
                        if room_bool:
                            raise ValidationError(
                                _(
                                    "Room %s cannot be reserved because"
                                    " it is occupy on these dates %s"
                                )
                                % (
                                    reservation_line.room_id.name,
                                    [
                                        str(date_overlap)
                                        for date_overlap in overlap_dates
                                    ],
                                )
                            )
                        else:
                            self.state = "confirm"
                            vals = {
                                "room_id": reservation_line.room_id.id,
                                "check_in": reservation.checkin,
                                "check_out": reservation.checkout,
                                "state": "assigned",
                                "reservation_id": reservation.id,
                                "reservation_line_id": reservation_line.id,
                            }
                            reservation_line.room_id.write(
                                {"isroom": False, "status": "occupied"}
                            )
                    else:
                        self.state = "confirm"
                        vals = {
                            "room_id": reservation_line.room_id.id,
                            "check_in": reservation.checkin,
                            "check_out": reservation.checkout,
                            "state": "assigned",
                            "reservation_id": reservation.id,
                            "reservation_line_id": reservation_line.id,
                        }
                        reservation_line.room_id.write(
                            {"isroom": False, "status": "occupied"}
                        )
                else:
                    self.state = "confirm"
                    vals = {
                        "room_id": reservation_line.room_id.id,
                        "check_in": reservation.checkin,
                        "check_out": reservation.checkout,
                        "state": "assigned",
                        "reservation_id": reservation.id,
                        "reservation_line_id": reservation_line.id,
                    }
                    reservation_line.room_id.write(
                        {"isroom": False, "status": "occupied"}
                    )
                reservation_line_obj.create(vals)
        return True

    def cancel_reservation(self):
        """
        This method cancel record set for hotel room reservation line
        ------------------------------------------------------------------
        @param self: The object pointer
        @return: cancel record set for hotel room reservation line.
        """
        wizard = self.env["hotel.reservation.cancel.wizard"].create(
            {"reservation_id": self.id}
        )
        return {
            "name": _("Cancel Reason"),
            "res_model": "hotel.reservation.cancel.wizard",
            "view_mode": "form",
            "res_id": wizard.id,
            "type": "ir.actions.act_window",
            "target": "new",
        }

    def set_to_draft_reservation(self):
        self.update({"state": "draft"})

    def action_send_reservation_mail(self):
        """
        This function opens a window to compose an email,
        template message loaded by default.
        @param self: object pointer
        """
        self.ensure_one(), "This is for a single id at a time."
        template_id = self.env.ref(
            "hotel_reservation.email_template_hotel_reservation"
        ).id
        compose_form_id = self.env.ref("mail.email_compose_message_wizard_form").id
        ctx = {
            "default_model": "hotel.reservation",
            "default_res_id": self.id,
            "default_use_template": bool(template_id),
            "default_template_id": template_id,
            "default_composition_mode": "comment",
            "force_send": True,
            "mark_so_as_sent": True,
        }
        return {
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "mail.compose.message",
            "views": [(compose_form_id, "form")],
            "view_id": compose_form_id,
            "target": "new",
            "context": ctx,
            "force_send": True,
        }

    @api.model
    def reservation_reminder_24hrs(self):
        """
        This method is for scheduler
        every 1day scheduler will call this method to
        find all tomorrow's reservations.
        ----------------------------------------------
        @param self: The object pointer
        @return: send a mail
        """
        now_date = fields.Date.today()
        template_id = self.env.ref(
            "hotel_reservation.mail_template_reservation_reminder_24hrs"
        )
        for reserv_rec in self:
            checkin_date = reserv_rec.checkin
            difference = relativedelta(now_date, checkin_date)
            if (
                difference.days == -1
                and reserv_rec.partner_id.email
                and reserv_rec.state == "confirm"
            ):
                template_id.send_mail(reserv_rec.id, force_send=True)
        return True

    def set_folio_draft(self):
        """Update folio and invoice state to draft"""
        # Update folio state to draft
        if self.folio_id.state == "sale":
            self.folio_id.action_folio_cancel()
            self.folio_id.order_id.action_draft()
            # Update invoice state to draft
            if (
                self.folio_id.hotel_invoice_id
                and self.folio_id.hotel_invoice_id.state != "draft"
            ):
                self.folio_id.hotel_invoice_id.button_draft()

    def post_folio_invoice(self, folio_state, invoice_state, payments):
        """post and confirm  folio and invoice"""
        # post invoice
        if self.folio_id.hotel_invoice_id:
            self.folio_id.hotel_invoice_id.with_context(
                check_move_validity=False
            )._recompute_tax_lines()
            self.folio_id.hotel_invoice_id.with_context(
                check_move_validity=False
            )._onchange_invoice_line_ids()
            if invoice_state == "posted":
                self.folio_id.hotel_invoice_id.action_post()
                # relate payment to invoice
                for line_id in payments.mapped("line_ids").filtered(
                    lambda line: line.account_internal_type in ("receivable", "payable")
                    and not line.reconciled
                ):
                    self.folio_id.hotel_invoice_id.js_assign_outstanding_line(
                        line_id.id
                    )
        # confirm  folio
        if folio_state == "sale":
            self.folio_id.action_confirm()

    def update_room_reservation_line(self, reservation_line, room, checkout):
        """Update Rooms reservation lines"""
        room_reservation_line = room.room_reservation_line_ids.filtered(
            lambda line: line.reservation_line_id.id == reservation_line.id
        )
        room_line_id = room.room_line_ids.filtered(
            lambda line: line.reservation_line_id.id == reservation_line.id
        )
        # update reservation (dates) in rooms
        if checkout:
            room_reservation_line.write({"check_out": checkout})
            room_line_id.write({"check_out": checkout})

    def update_folio_invoice(self, room_line, room, checkout, duration, is_change_rent):
        """Update folio and invoice"""
        if room_line.reservation_line_id:
            # Update Rooms and folio reservation lines
            room_line.write(
                {
                    "checkout_date": checkout,
                    "product_uom_qty": int(duration),
                }
            )
            self.update_room_reservation_line(
                room_line.reservation_line_id, room, checkout
            )
            # update invoice qty
            if self.folio_id.hotel_invoice_id:
                room_line.invoice_lines.with_context(
                    check_move_validity=False
                ).quantity = duration
            if is_change_rent or room_line.reservation_line_id.peak_days:
                # update price unit in folio and invoice
                price_unit = self.get_price(
                    room_line.reservation_line_id.other_price,
                    self.rent,
                    room,
                    self.company_id,
                    room_line.checkin_date,
                    checkout,
                    duration,
                )
                # update prices
                room_line.price_unit = price_unit
                if room_line.reservation_line_id.line_id.folio_id.hotel_invoice_id:
                    room_line.invoice_lines.with_context(
                        check_move_validity=False
                    ).write({"price_unit": price_unit})

    def get_discount_insurance(
        self, folio_line, invoice_line, checkin, checkout, product, price_unit, name
    ):
        """Update insurance and discount in reservation"""
        # update unit price if there is a line in folio
        if folio_line:
            folio_line[0].price_unit = price_unit
        else:
            # create new folio line if there is a no line in folio
            if product:
                folio_line = self.env["hotel.folio.line"].create(
                    {
                        "checkin_date": checkin,
                        "folio_id": self.folio_id.id,
                        "checkout_date": checkout,
                        "product_id": product.id,
                        "name": name,
                        "price_unit": price_unit,
                        "product_uom_qty": 1,
                        "is_reserved": True,
                    }
                )

        folio_line._onchange_product_id()
        folio_line.price_unit = price_unit
        if self.folio_id.hotel_invoice_id:
            if invoice_line:
                # update unit price if there is a line in invoice
                invoice_line[0].with_context(
                    check_move_validity=False
                ).price_unit = price_unit
            else:
                # create new invoice line if there is a no line in invoice
                accounts = False
                fiscal_position = self.folio_id.hotel_invoice_id.fiscal_position_id
                if fiscal_position:
                    accounts = product.product_tmpl_id.with_company(
                        self.company_id
                    ).get_product_accounts(fiscal_pos=fiscal_position)
                invoice = self.folio_id.hotel_invoice_id
                invoice_line = (
                    self.env["account.move.line"]
                    .with_context(check_move_validity=False)
                    .create(
                        {
                            "product_id": product.id,
                            "quantity": 1,
                            "price_unit": price_unit,
                            "move_id": self.folio_id.hotel_invoice_id.id,
                            "account_id": accounts["income"].id
                            if accounts
                            else invoice.journal_id.default_account_id.id,
                        }
                    )
                )

                invoice_line.with_context(
                    check_move_validity=False
                )._onchange_product_id()
                invoice_line.with_context(
                    check_move_validity=False
                ).price_unit = price_unit
                self.folio_id.hotel_invoice_id.with_context(
                    check_move_validity=False
                ).invoice_line_ids += invoice_line
                folio_line.invoice_lines = [
                    (
                        4,
                        invoice_line.id,
                    )
                ]

    def update_discount_folio_invoice(self, reservation_line_id):
        """Update discount"""
        discount_product = self.env["product.product"].search(
            [("discount", "=", True)], limit=1
        )
        folio_discount = self.folio_id.room_line_ids.filtered(
            lambda discount_line: discount_line.product_id.discount
        )
        line_discount = self.folio_id.hotel_invoice_id.invoice_line_ids.filtered(
            lambda discount_line: discount_line.product_id.discount
        )
        # calculate discount
        self.get_discount_insurance(
            folio_discount,
            line_discount,
            self.checkin,
            reservation_line_id.date_extension
            if reservation_line_id and reservation_line_id.date_extension
            else self.checkout,
            discount_product,
            -(self.discount + self.discount_change_room)
            if not self.is_hospitality
            else -(self.discount + self.discount_change_room + self.taxes_amount),
            _("Discount"),
        )

    def update_returnable_folio_invoice(self, reservation_line_id):
        """Update returnable"""
        returnable_product = self.env["product.product"].search(
            [("returnable", "=", True)], limit=1
        )
        folio_returnable = self.folio_id.room_line_ids.filtered(
            lambda returnable_line: returnable_line.product_id.returnable
        )
        line_returnable = self.folio_id.hotel_invoice_id.invoice_line_ids.filtered(
            lambda returnable_line: returnable_line.product_id.returnable
        )
        self.get_discount_insurance(
            folio_returnable,
            line_returnable,
            self.checkin,
            reservation_line_id.date_extension
            if reservation_line_id and reservation_line_id.date_extension
            else self.checkout,
            returnable_product,
            self.returnable_amount,
            _("Returnable"),
        )

    def update_discount_insurance_returnable_folio(
        self, discount, returnable, reservation_line_id
    ):
        """Update Insurance, amount returnable and discount in folio and invoice."""
        # Update discount
        folio_discount = self.folio_id.room_line_ids.filtered(
            lambda discount_line: discount_line.product_id.discount
        )
        if discount or folio_discount:
            self.update_discount_folio_invoice(reservation_line_id)
        # Update returnable
        if returnable:
            self.update_returnable_folio_invoice(reservation_line_id)

    def create_folio_line(
        self,
        folio,
        reservation_line_id,
        room,
        checkin,
        checkout,
        duration,
        price_unit,
        discount,
        insurance,
    ):
        """Create lines in folio and invoice"""
        # create new folio line if there is a change rooms
        line = self.env["hotel.folio.line"].create(
            {
                "reservation_line_id": reservation_line_id.id,
                "checkin_date": checkin,
                "folio_id": folio.id,
                "checkout_date": checkout,
                "product_id": room.product_id and room.product_id.id,
                "name": self["reservation_no"],
                "price_unit": price_unit,
                "product_uom_qty": duration,
                "is_reserved": True,
            }
        )
        line._onchange_product_id()
        line.price_unit = price_unit

        # Create line invoice
        if folio.hotel_invoice_id:
            accounts = False
            fiscal_position = folio.hotel_invoice_id.fiscal_position_id
            if fiscal_position:
                accounts = room.product_id.product_tmpl_id.with_company(
                    self.company_id
                ).get_product_accounts(fiscal_pos=fiscal_position)
            # create new invoice line if there is a change rooms
            line_invoice = (
                self.env["account.move.line"]
                .with_context(check_move_validity=False)
                .create(
                    {
                        "product_id": room.product_id.id,
                        "quantity": duration,
                        "price_unit": price_unit,
                        "move_id": folio.hotel_invoice_id.id,
                        "account_id": accounts["income"].id
                        if accounts
                        else folio.hotel_invoice_id.journal_id.default_account_id.id,
                    }
                )
            )
            line_invoice.with_context(check_move_validity=False)._onchange_product_id()
            line_invoice.with_context(check_move_validity=False).tax_ids = line.tax_id
            line_invoice.with_context(check_move_validity=False).price_unit = price_unit
            line.invoice_lines = [
                (
                    4,
                    line_invoice.id,
                )
            ]

            # update insurance and discount and returnable amount in folio and invoice
        self.update_discount_insurance_returnable_folio(
            discount, self.returnable_amount, reservation_line_id
        )

    def prepare_folio_lines(
        self, reservation, folio_lines, checkin_date, checkout_date
    ):
        """Prepare folio lines."""
        for line in reservation.reservation_line:
            # Calculate price room based on rent type
            # for room in line.reserve:
            if line.line_id.rent == "daily":
                price_unit = line.room_id.list_price
            elif line.line_id.rent == "monthly":
                price_unit = line.room_id.monthly_price
            else:
                price_unit = line.room_id.hourly_price
            # get peak price
            peak_price = line.calculate_peak_room_price(
                reservation.rent,
                line.room_id,
                reservation.company_id.id,
                reservation.checkin,
                reservation.checkout,
                reservation.duration,
            )
            price_unit = peak_price if peak_price else price_unit
            if line.is_minimum_price or line.is_other_price:
                price_unit = line.other_price
            folio_lines.append(
                (
                    0,
                    0,
                    {
                        "reservation_line_id": line.id,
                        "checkin_date": checkin_date,
                        "checkout_date": checkout_date,
                        "product_id": line.room_id.product_id
                        and line.room_id.product_id.id,
                        "name": reservation["reservation_no"],
                        "price_unit": price_unit,
                        "product_uom_qty": reservation.duration,
                        "is_reserved": True,
                    },
                )
            )
            line.room_id.write({"status": "occupied", "isroom": False})
        # Calculate discount
        if reservation.discount:
            discount_product = self.env["product.product"].search(
                [("discount", "=", True)], limit=1
            )
            folio_lines.append(
                (
                    0,
                    0,
                    {
                        "checkin_date": checkin_date,
                        "checkout_date": checkout_date,
                        "product_id": discount_product and discount_product.id,
                        "name": _("Discount"),
                        "price_unit": -reservation.discount
                        if not self.is_hospitality
                        else -(
                            reservation.discount
                            + reservation.discount_change_room
                            + reservation.taxes_amount
                        ),
                        "product_uom_qty": 1,
                    },
                )
            )
        # Calculate returnable
        if reservation.is_returnable and reservation.returnable_amount:
            returnable_product = self.env["product.product"].search(
                [("returnable", "=", True)], limit=1
            )
            folio_lines.append(
                (
                    0,
                    0,
                    {
                        "checkin_date": checkin_date,
                        "checkout_date": checkout_date,
                        "product_id": returnable_product and returnable_product.id,
                        "name": _("Recovery"),
                        "price_unit": reservation.returnable_amount,
                        "product_uom_qty": 1,
                    },
                )
            )
        return folio_lines

    def create_folio(self):
        """
        This method is for create new hotel folio.
        -----------------------------------------
        @param self: The object pointer
        @return: new record set for hotel folio.
        """
        hotel_folio_obj = self.env["hotel.folio"]
        for reservation in self:
            folio_lines = []
            checkin_date = reservation["checkin"]
            checkout_date = reservation["checkout"]
            warehouse = reservation.env["stock.warehouse"].search(
                [("company_id", "=", reservation.company_id.id)], limit=1
            )
            # prepare folio vals
            folio_vals = {
                "date_order": reservation.date_order,
                "company_id": reservation.company_id.id,
                "warehouse_id": warehouse.id,
                "partner_id": reservation.partner_id.id,
                "partner_invoice_id": reservation.partner_invoice_id.id,
                "partner_shipping_id": reservation.partner_shipping_id.id,
                "checkin_date": reservation.checkin,
                "checkout_date": reservation.checkout,
                "duration": reservation.duration,
                "reservation_id": reservation.id,
            }
            folio_lines = reservation.prepare_folio_lines(
                reservation, folio_lines, checkin_date, checkout_date
            )
            folio_vals.update({"room_line_ids": folio_lines})
            # create folio
            folio = hotel_folio_obj.create(folio_vals)
            for rm_line in folio.room_line_ids:
                price_unit = rm_line.price_unit
                rm_line._onchange_product_id()
                rm_line.price_unit = price_unit
            self.write({"folio_id": [(6, 0, folio.ids)], "state": "done"})
        return True

    def send_shomoos(self):
        """send to shomoos."""
        self.write({"is_send_shomoos": not self.is_send_shomoos})

    def send_tourism(self):
        """send to tourism."""
        self.write({"is_send_tourism": not self.is_send_tourism})

    def get_duration(self, rent, date_from, date_to):
        """Calculate duration."""
        if rent == "daily":
            if date_from.date() == date_to.date():
                duration = 1
            else:
                duration = (date_to.date() - date_from.date()).days

        elif rent == "monthly":
            duration = (date_to.date() - date_from.date()).days / 30
        else:
            duration = (date_to - date_from).total_seconds() / 3600
        return round(duration)

    def open_folio_view(self):
        folios = self.mapped("folio_id")
        action = self.env.ref("hotel.open_hotel_folio1_form_tree_all").sudo().read()[0]
        if len(folios) > 1:
            action["domain"] = [("id", "in", folios.ids)]
        elif len(folios) == 1:
            action["views"] = [(self.env.ref("hotel.view_hotel_folio_form").id, "form")]
            action["res_id"] = folios.id
        else:
            action = {"type": "ir.actions.act_window_close"}
        return action

    @api.onchange("checkin", "checkout", "rent")
    def _onchange_checkin_checkout(self):
        """Calculate duration"""
        self.duration = 0
        if self.checkin and self.checkout:
            self.duration = self.get_duration(self.rent, self.checkin, self.checkout)
            if not self._context.get("default_type_state") and not (
                self.checkin.date() == self.checkout.date() and self.rent == "daily"
            ):
                self._onchange_duration()

    def get_hour_setting(self):
        """Get hour setting"""
        hour, minute = 0, 0
        hour_setting = self.env["hotel.reservation.setting"].search(
            [("company_id", "=", self.company_id.id)], limit=1
        )
        if hour_setting and hour_setting.hours_day:
            hour, minute = self.get_hour_minute_float(hour_setting.hours_day)
        return hour_setting, hour, minute

    @api.onchange("duration", "rent")
    def _onchange_duration(self):
        if self.duration:
            hour_setting, hour, minute = self.get_hour_setting()
            # calculate checkout and check in
            checkout = self.checkout
            self.checkout = 0
            if self.rent == "daily":
                if (
                    self.duration == 1
                    and checkout
                    and self.checkin.date() == checkout.date()
                ):
                    checkin = self.checkin
                else:
                    checkin = self.checkin + relativedelta(days=int(self.duration))
            elif self.rent == "monthly":
                checkin = self.checkin + relativedelta(days=int(self.duration * 30))
            else:
                checkin = self.checkin + relativedelta(hours=int(self.duration))
            # change checkout date based on hour setting
            if hour_setting and self.rent in ["daily", "monthly"]:
                tz_diff = (
                    checkin.astimezone(pytz.timezone("Asia/Riyadh")).replace(
                        tzinfo=None
                    )
                    - checkin
                )
                tz_diff = tz_diff.seconds / 3600
                checkin = checkin.replace(
                    hour=hour - int(tz_diff), minute=minute, second=0
                )
            self.checkout = checkin

    def get_price(
        self, other_price, rent, room_id, company, checkin, checkout, duration
    ):
        """Get room price"""
        if rent == "daily":
            price = room_id.list_price
        elif rent == "monthly":
            price = room_id.monthly_price
        else:
            price = room_id.hourly_price
        # calculate peak price
        peak_price = self.env["hotel.reservation.line"].calculate_peak_room_price(
            rent,
            room_id,
            company.id,
            checkin,
            checkout,
            duration,
        )
        price_room = peak_price if peak_price else price
        return other_price if other_price else price_room

    def get_duration_change_room(self, date_from, date_to, rent):
        """Get duration for change rooms"""
        if rent == "daily":
            duration = (date_to.date() - date_from.date()).days
            if date_to.date() == date_from.date():
                duration = +1
        elif rent == "monthly":
            duration = (date_to.date() - date_from.date()).days / 30
        else:
            duration = (date_to - date_from).total_seconds() / 3600
        return round(duration)

    def calculate_old_room_prices(self, reservation, line, rent):
        """Calculate price and duration and taxesold rooms"""
        all_price = 0
        taxes_amount = 0
        all_duration = 1
        for history in reservation.env["reservation.room.change.history"].search(
            [("reservation_line_id", "=", line.id), ("is_no_calculated", "=", False)]
        ):
            if rent == "hours" or (
                rent in ["daily", "monthly"]
                and history.change_date.date() != history.reservation_date.date()
            ):
                duration = reservation.get_duration_change_room(
                    history.reservation_date, history.change_date, rent
                )
                price = reservation.get_price(
                    history.old_other_price,
                    rent,
                    history.old_room_id,
                    reservation.company_id,
                    history.reservation_date,
                    history.change_date + relativedelta(days=int(-1)),
                    duration,
                )
                all_duration += duration
                taxes = history.old_room_id.taxes_id.compute_all(
                    price,
                    history.old_room_id.currency_id,
                    duration,
                    product=history.old_room_id.product_id,
                    partner=reservation.partner_shipping_id,
                )
                taxes_amount += sum(
                    tax.get("amount", 0.0) for tax in taxes.get("taxes", [])
                )
                all_price += taxes["total_excluded"]
        return all_price, int(all_duration) - 1, taxes_amount, taxes

    @api.onchange("reservation_line")
    def _onchange_reservation_line(self):
        """Calculate insurance."""
        insurance = 0
        for room in self.reservation_line.mapped("room_id"):
            insurance += room.insurance
        self.insurance = (
            self.insurance_change_room if self.insurance_change_room else insurance
        )

    @api.depends(
        "reservation_line",
        "reservation_line.total_room_rate",
        "reservation_line.other_price",
        "reservation_line.peak_price",
        "reservation_line.peak_days",
        "duration",
        "discount_type",
        "discount_percentage",
        "returnable_percentage",
        "discount",
        "insurance",
        "reservation_line.discount_change_room",
        "insurance_change_room",
        "reservation_line.date_extension",
        "service_amount",
        "rent",
        "checkin",
        "checkout",
    )
    def _compute_total_room_rate(self):
        """Calculate Costs."""
        for reservation in self:
            taxes_amount = 0
            taxes_info = {}
            reservation.taxes_info = ""
            reservation.room_rate = reservation.total_room_rate = 0
            for line in reservation.reservation_line:
                duration = (
                    reservation.duration
                    if not line.date_extension
                    else line.duration_extension
                )
                history = reservation.history_room_ids.filtered(
                    lambda history: history.reservation_line_id.id == line.id
                    and not history.is_no_calculated
                )
                room = line.room_id
                other_price = line.other_price
                checkin = reservation.checkin
                checkout = (
                    line.date_extension if line.date_extension else reservation.checkout
                )
                if (
                    line.date_termination
                    and reservation.reservation_type == "collective"
                    and reservation.is_returnable
                ):
                    duration = line.duration_termination
                    checkout = line.date_termination
                # Get duration and taxes and prices of old rooms
                # when change rooms that we didn't terminate it
                old_room_taxes = False
                if len(history):
                    if line.date_termination:
                        history = reservation.history_room_ids.filtered(
                            lambda history: history.reservation_line_id.id == line.id
                            and not history.is_no_calculated
                            and history.change_date.date()
                            <= line.date_termination.date()
                        )
                    if history:
                        room = history[-1].room_id
                        other_price = history[-1].other_price
                        (
                            all_price,
                            all_duration,
                            taxes_amount_change,
                            old_room_taxes,
                        ) = reservation.calculate_old_room_prices(
                            reservation, line, reservation.rent
                        )
                        checkin = history[-1].change_date
                        duration = reservation.get_duration_change_room(
                            history[-1].change_date, checkout, reservation.rent
                        )
                        if reservation.rent == "daily":
                            duration = duration
                price = reservation.get_price(
                    other_price,
                    reservation.rent,
                    room,
                    reservation.company_id,
                    checkin,
                    checkout,
                    duration,
                )
                taxes = room.taxes_id.compute_all(
                    price,
                    room.currency_id,
                    duration,
                    product=room.product_id,
                    partner=reservation.partner_shipping_id,
                )
                # calculte amount tax and tax info
                all_taxes = taxes.get("taxes", [])
                if old_room_taxes and old_room_taxes.get("taxes", []):
                    all_taxes += list(old_room_taxes.get("taxes", []))
                for tax in all_taxes:
                    if str(tax.get("name")) not in taxes_info:
                        taxes_info[str(tax.get("name"))] = tax.get("amount")
                    else:
                        taxes_info[str(tax.get("name"))] = taxes_info.get(
                            str(tax.get("name"))
                        ) + tax.get("amount")
                    taxes_amount += tax.get("amount", 0.0)

                if len(history):
                    reservation.total_room_rate += taxes["total_excluded"] + all_price
                    price = (
                        (taxes["total_excluded"] + all_price)
                        / (duration + all_duration)
                        if (duration + all_duration)
                        else 0
                    )
                    reservation.room_rate += price
                    duration = (
                        reservation.duration
                        if not line.date_extension
                        else line.duration_extension
                    )
                else:
                    reservation.total_room_rate += taxes["total_excluded"]
                    reservation.room_rate += price
            # tax info
            for tax_info in taxes_info:
                reservation.taxes_info += "%s : %s \n" % (
                    tax_info,
                    "%.2f" % taxes_info.get(tax_info),
                )
            reservation.total_room_rate += reservation.service_amount
            reservation.discount = (
                reservation.discount
                if reservation.discount_type == "amount"
                else (reservation.discount_percentage * reservation.total_room_rate)
                / 100
            )
            # calculate discount when change rooms
            reservation.discount_change_room = sum(
                reservation.reservation_line.mapped("discount_change_room")
            )
            reservation.total_cost = (
                reservation.total_room_rate
                - reservation.discount
                - reservation.discount_change_room
            )

            reservation.taxes_amount = taxes_amount + reservation.service_tax

            reservation.taxed_total_rate = (
                (reservation.taxes_amount + reservation.total_cost)
                if not reservation.is_hospitality
                else 0
            )
            reservation.returnable_amount = (
                reservation.taxed_total_rate * reservation.returnable_percentage
            ) / 100
            reservation.final_cost = (
                (
                    reservation.taxed_total_rate
                    + reservation.insurance
                    + reservation.returnable_amount
                )
                if not reservation.is_hospitality
                else 0
            )

    @api.model
    def cron_change_room_reservation_daily(self):
        """Cron for termination and change rooms"""
        change_room_reservation = self.env["reservation.room.change.history"].search(
            [("is_no_calculated", "=", False)]
        )
        # for change rooom ( change room and update room state)
        for history in change_room_reservation.filtered(
            lambda history: (
                history.reservation_line_id.line_id.rent != "hours"
                and history.change_date.date() == datetime.today().date()
            )
        ):
            history.reservation_line_id.room_id.write(
                {"is_clean": False, "status": "available"}
            )
            history.reservation_line_id.room_id = history.room_id.id
            history.reservation_line_id.other_price = history.other_price
            if history.reservation_id.reservation_type == "individual":
                history.reservation_id.partner_id.last_room_id = (
                    history.reservation_line_id.room_id.id
                )
            else:
                partner = (
                    history.reservation_line_id.partner_id
                    if history.reservation_line_id.tenant == "person"
                    else history.reservation_line_id.partner_company_id
                )
                partner.last_room_id = history.reservation_line_id.room_id.id
            history.reservation_line_id.room_id.status = "occupied"

    @api.model
    def cron_change_room_reservation_hours(self):
        """Cron for termination and change rooms"""
        change_room_reservation = self.env["reservation.room.change.history"].search(
            [("is_no_calculated", "=", False)]
        )
        for history in change_room_reservation.filtered(
            lambda history: (
                history.reservation_line_id.line_id.rent == "hours"
                and history.change_date.date() == datetime.today().date()
                and history.change_date.hour == datetime.today().hour
            )
        ):
            history.reservation_line_id.room_id.write(
                {"is_clean": False, "status": "available"}
            )
            history.reservation_line_id.room_id = history.room_id.id
            history.reservation_line_id.room_id = history.other_price
            history.reservation_line_id.room_id.status = "occupied"

    @api.depends("payment_ids.amount", "payment_ids.support_type_id", "payment_ids.payment_type", "payment_ids.state")
    def _compute_payment_totals(self):
        for reservation in self:
            totals = {'inbound': {}, 'outbound': {}}
            # Initialize new fields for tracking insurance payments
            inbound_insurance_total = 0.0
            outbound_insurance_total = 0.0
            inbound_total = 0.0
            outbound_total = 0.0

            for payment in reservation.payment_ids: # .filtered(lambda p: p.state == "posted")
                payment_type = payment.payment_type  # 'inbound' or 'outbound'
                support_type = payment.support_type_id.name
                
                # Sum total amounts for inbound and outbound
                if payment_type == 'inbound':
                    if support_type == "Advance Insurance":  
                        inbound_insurance_total += payment.amount
                    else:
                        inbound_total += payment.amount
                elif payment_type == 'outbound': 
                    if support_type == "Insurance Refund":
                        outbound_insurance_total -= payment.amount
                    else:
                        outbound_total -= payment.amount 

                # Initialize and sum amounts for each support type within payment type
                if support_type not in totals[payment_type]:
                    totals[payment_type][support_type] = 0.0
                totals[payment_type][support_type] += payment.amount

            # Assign totals to the fields
            reservation.total_inbound_payments = inbound_total
            reservation.total_inbound_insurance = inbound_insurance_total
            reservation.total_outbound_payments = abs(outbound_total)
            reservation.total_outbound_insurance = abs(outbound_insurance_total)

            # Optionally, you can still format the detailed totals for display if needed
            formatted_totals = []
            for payment_type, supports in totals.items():
                for support_type, amount in supports.items():
                    formatted_totals.append(f"{payment_type.capitalize()} - {support_type}: {amount}")
            
            reservation.payment_totals = "\n".join(formatted_totals)

    # @api.depends("payment_ids.amount", "payment_ids.support_type_id", "payment_ids.payment_type", "payment_ids.state")
    # def _compute_payment_totals(self):
    #     for reservation in self:
    #         totals = {'inbound': {}, 'outbound': {}}
    #         inbound_total = 0.0
    #         outbound_total = 0.0
            
    #         for payment in reservation.payment_ids.filtered(lambda p: p.state == "posted"):
    #             payment_type = payment.payment_type  # 'inbound' or 'outbound'
    #             support_type = payment.support_type_id.name
                
    #             # Sum total amounts for inbound and outbound
    #             if payment_type == 'inbound':
    #                 inbound_total += payment.amount
    #             elif payment_type == 'outbound':
    #                 outbound_total -= payment.amount  # Assuming outbound is a negative flow
                
    #             # Initialize and sum amounts for each support type within payment type
    #             if support_type not in totals[payment_type]:
    #                 totals[payment_type][support_type] = 0.0
    #             totals[payment_type][support_type] += payment.amount

    #         # Assign totals to the new fields
    #         reservation.total_inbound_payments = inbound_total
    #         reservation.total_outbound_payments = outbound_total

    #         # Format the detailed totals for display
    #         formatted_totals = []
    #         for payment_type, supports in totals.items():
    #             for support_type, amount in supports.items():
    #                 formatted_totals.append(f"{payment_type.capitalize()} - {support_type}: {amount}")
            
    #         reservation.payment_totals = "\n".join(formatted_totals)


    @api.depends(
        "partner_id.invoice_ids.amount_residual",
        "folio_id",
        "partner_id",
        "payment_ids",
        "payment_ids.state",
        "folio_id.hotel_invoice_id",
        "folio_id.hotel_invoice_id.payment_state",
        "folio_id.hotel_invoice_id.state",
        "folio_id.hotel_invoice_id.reversal_move_id",
        "folio_id.hotel_invoice_id.reversal_move_id.amount_residual",
        "folio_id.hotel_invoice_id.line_ids",
        "folio_id.hotel_invoice_id.line_ids.amount_residual",
        "final_cost",
    )
    def _compute_payments(self):
        """Calculate payments and balance and payments details ."""
        for reservation in self:
            reservation.balance = (
                reservation.payments_count
            ) = reversed_entry_payment = 0
            if reservation.folio_id.hotel_invoice_id:
                if reservation.folio_id.hotel_invoice_id.reversal_move_id:
                    # flake8: noqa: B950
                    for (
                        reversal_move
                    ) in reservation.folio_id.hotel_invoice_id.reversal_move_id:
                        reversed_entry_payment += sum(
                            payment_reversed["amount"]
                            for payment_reversed in reversal_move._get_reconciled_info_JSON_values()
                        )
                # flake8: noqa: B950
                reservation.payments_count = (
                    sum(
                        payment["amount"]
                        for payment in reservation.folio_id.hotel_invoice_id._get_reconciled_info_JSON_values()
                    )
                    - reversed_entry_payment
                )
            # calculate payment based on payments of reservation
            payments_supplier_amount = sum(
                reservation.payment_ids.filtered(
                    lambda payment_reservation: payment_reservation.payment_type
                    == "outbound"
                    and payment_reservation.state == "posted"
                ).mapped("amount")
            )

            payments = reservation.payment_ids.filtered(
                lambda payment_reservation: payment_reservation.payment_type
                == "inbound"
                and payment_reservation.state == "posted"
            )
            if payments:
                reservation.payments_count = sum(payments.mapped("amount"))
            # calculate balance
            reservation.balance = (
                reservation.payments_count
                - (reservation.final_cost - reservation.insurance)
                - payments_supplier_amount
            )

    @api.depends("date_check_in", "date_check_out", "rent")
    def _compute_check_duration(self):
        """Calculate Check Duration."""
        for reservation in self:
            reservation.duration_check = 0
            if reservation.date_check_in and reservation.date_check_out:
                reservation.duration_check = reservation.get_duration(
                    reservation.rent,
                    reservation.date_check_in,
                    reservation.date_check_out,
                )

    def _compute_display_button_reservation(self):
        """Display buttons reservation."""
        for reservation in self:
            reservation.display_button_terminate_reservation = (
                reservation.display_button_extend_reservation
            ) = (
                reservation.display_button_check_in_reservation
            ) = (
                reservation.display_button_check_out_reservation
            ) = (
                reservation.display_button_cancel
            ) = reservation.display_button_returned_reservation = False
            today = (
                datetime.today()
                if reservation.rent == "hours"
                else datetime.today().date()
            )
            checkin = (
                reservation.checkin
                if reservation.rent == "hours"
                else reservation.checkin.date()
            )
            checkout = (
                reservation.checkout
                if reservation.rent == "hours"
                else reservation.checkout.date()
            )
            date_termination = False
            if reservation.date_termination:
                date_termination = (
                    reservation.date_termination
                    if reservation.rent == "hours"
                    else reservation.date_termination.date()
                )
            # display button cancel
            if reservation.state in ["draft", "confirm"]:
                reservation.display_button_cancel = True
            if reservation.state == "done":
                # display button terminate
                if (
                    reservation.reservation_type == "individual"
                    and not reservation.date_check_out
                    and not reservation.date_termination
                    and reservation.date_check_in
                    and (
                        (
                            reservation.checkin
                            < datetime.today()
                            < reservation.checkout
                            and reservation.rent == "hours"
                        )
                        or (
                            reservation.checkin < datetime.today()
                            and datetime.today().date() < reservation.checkout.date()
                            and reservation.rent != "hours"
                        )
                    )
                ) or (
                    reservation.reservation_type == "collective"
                    and reservation.reservation_line.filtered(
                        lambda line: not line.date_termination
                        and line.date_check_in
                        and not line.date_check_out
                        and (
                            (
                                not line.date_extension
                                and reservation.checkin
                                < datetime.today()
                                < reservation.checkout
                            )
                            or (
                                line.date_extension
                                and reservation.checkin
                                < datetime.today()
                                < line.date_extension
                            )
                        )
                    )
                ):
                    reservation.display_button_terminate_reservation = True
                # display button extension
                if not reservation.is_returnable_reservation and (
                    (
                        reservation.reservation_type == "individual"
                        and not reservation.date_check_out
                        and not reservation.date_termination
                        and (
                            (date_termination and date_termination >= today)
                            or checkout >= today
                        )
                    )
                    or (
                        reservation.reservation_line.filtered(
                            lambda line: not line.date_check_out
                            and not line.date_termination
                            and (
                                (
                                    (
                                        reservation.rent != "hours"
                                        and line.date_termination
                                        and line.date_termination.date()
                                        >= datetime.today().date()
                                    )
                                    or (
                                        reservation.rent == "hours"
                                        and line.date_termination
                                        and line.date_termination >= datetime.today()
                                    )
                                )
                                or (
                                    (
                                        reservation.rent != "hours"
                                        and not line.date_extension
                                        and line.line_id.checkout.date()
                                        >= datetime.today().date()
                                    )
                                    or (
                                        reservation.rent == "hours"
                                        and not line.date_extension
                                        and line.line_id.checkout >= datetime.today()
                                    )
                                )
                                or (
                                    (
                                        reservation.rent != "hours"
                                        and line.date_extension
                                        and line.date_extension.date()
                                        >= datetime.today().date()
                                    )
                                    or (
                                        reservation.rent == "hours"
                                        and line.date_extension
                                        and line.date_extension.date()
                                        >= datetime.today().date()
                                    )
                                )
                            )
                        )
                        and reservation.reservation_type == "collective"
                    )
                ):
                    reservation.display_button_extend_reservation = True
                # display button check in
                if (
                    (
                        not reservation.date_check_in
                        and reservation.reservation_type == "individual"
                    )
                    or (
                        reservation.reservation_line.filtered(
                            lambda line: not line.date_check_in
                        )
                        and reservation.reservation_type == "collective"
                    )
                ) and checkin <= today <= checkout:
                    reservation.display_button_check_in_reservation = True
                # display button check out
                if (
                    reservation.date_check_in
                    and not reservation.date_check_out
                    and reservation.reservation_type == "individual"
                    and (
                        (today >= checkout and not reservation.date_termination)
                        or (
                            reservation.rent != "hours"
                            and reservation.date_termination
                            and datetime.today().date()
                            >= reservation.date_termination.date()
                        )
                        or (
                            reservation.rent == "hours"
                            and reservation.date_termination
                            and datetime.today() >= reservation.date_termination
                        )
                    )
                ) or (
                    reservation.reservation_line.filtered(
                        lambda line: not line.date_check_out
                        and line.date_check_in
                        and (
                            (
                                reservation.rent != "hours"
                                and (
                                    (
                                        line.date_termination
                                        and datetime.today().date()
                                        >= line.date_termination.date()
                                    )
                                    or (
                                        not line.date_termination
                                        and (
                                            (
                                                reservation.checkout.date()
                                                <= datetime.today().date()
                                                and not line.date_extension
                                            )
                                            or (
                                                line.date_extension
                                                and line.date_extension.date()
                                                <= datetime.today().date()
                                            )
                                        )
                                    )
                                )
                            )
                            or (
                                reservation.rent == "hours"
                                and (
                                    (
                                        line.date_termination
                                        and datetime.today() >= line.date_termination
                                    )
                                    or (
                                        not line.date_termination
                                        and (
                                            (
                                                reservation.checkout <= datetime.today()
                                                and not line.date_extension
                                            )
                                            or (
                                                line.date_extension
                                                and line.date_extension
                                                <= datetime.today()
                                            )
                                        )
                                    )
                                )
                            )
                        )
                    )
                    and reservation.reservation_type == "collective"
                ):
                    reservation.display_button_check_out_reservation = True

                # display button cancel
                if (
                    not reservation.date_check_in
                    and reservation.reservation_type == "individual"
                ) or (
                    len(
                        reservation.reservation_line.filtered(
                            lambda line: not line.date_check_in
                        )
                    )
                    == len(reservation.reservation_line)
                    and reservation.reservation_type == "collective"
                ):
                    reservation.display_button_cancel = True
            # display button returned reservation
            if (
                reservation.is_returnable
                and not reservation.is_returnable_reservation
                and (
                    reservation.state == "cancel"
                    or (
                        reservation.state == "done"
                        and reservation.reservation_line.filtered(
                            lambda line: line.date_termination
                        )
                    )
                )
            ):
                reservation.display_button_returned_reservation = True

    @api.onchange("children_ids")
    def _onchange_children_adults(self):
        self.children = len(self.children_ids)

    @api.onchange("reservation_type")
    def _onchange_reservation_type(self):
        if self.reservation_type:
            self.adults = False
            self.children = False
            self.children_ids = False
            self.adults_ids = False

    @api.onchange("source_id")
    def _onchange_source(self):
        if self.source_id:
            self.source_number = ""

    @api.constrains("discount_type")
    def _check_discount_type(self):
        """Check reservation percentage and amount."""
        for reservation in self:
            if (
                reservation.discount_type == "percentage"
                and not reservation.discount_percentage
            ):
                raise ValidationError(_("You should add discount percentage"))
            if reservation.discount_type == "amount" and not reservation.discount:
                raise ValidationError(_("You should add discount amount"))

    def get_hijri_date(self, georging_date, separator):
        """Convert georging date to hijri date.

        :return hijri date as a string value
        """
        if georging_date:
            georging_date = georging_date.date()
            georging_date = fields.Date.from_string(georging_date)
            hijri_date = HijriDate(
                georging_date.year, georging_date.month, georging_date.day, gr=True
            )
            return (
                str(int(hijri_date.year)).zfill(2)
                + separator
                + str(int(hijri_date.month)).zfill(2)
                + separator
                + str(int(hijri_date.day))
            )
        return None

    def button_returned_reservation(self):
        self.is_returnable_reservation = True

    def action_terminate_extend_reservation(self):
        """Terminate and extend Reservation."""
        wizard = self.env["hotel.reservation.finish.wizard"].create(
            {"reservation_id": self.id, "origin_rent": self.rent}
        )
        if self._context.get("default_type_state") == "finish":
            wizard.type = "finish"
            name = _("Termination Reservation")
        else:

            wizard.type = "extension"
            name = _("Extend Reservation")
        return {
            "name": name,
            "res_model": "hotel.reservation.finish.wizard",
            "view_mode": "form",
            "res_id": wizard.id,
            "type": "ir.actions.act_window",
            "target": "new",
            "context": {"default_type_reservation": self.reservation_type},
        }

    def create_post_invoice(self):
        """Create and post invoice"""
        if self.folio_id.state != "sale":
            self.folio_id.action_confirm()
        if not self.folio_id.hotel_invoice_id:
            self.folio_id.create_invoices()
        invoice = self.folio_id.hotel_invoice_id
        invoice.action_post()

    def update_folio_invoice_qty(self, room_line):
        # update folio and invoice line based on setting hours
        if room_line.product_uom_qty:
            room = self.env["hotel.room"].search(
                [("product_id", "=", room_line.product_id.id)], limit=1
            )
            self.update_folio_invoice(
                room_line,
                room,
                room_line.checkout_date,
                room_line.product_uom_qty + 1,
                False,
            )

    def action_payment_create(self, payment_type, partner_type, account):
        """Create payment"""
        journal = self.env["account.journal"].search([("type", "=", "bank")], limit=1)
        payment_method_id = (
            self.env["account.payment.method"]
            .search([("payment_type", "=", payment_type)], limit=1)
            .id
        )
        other_payments = self.payment_ids.filtered(
            lambda payment_reservation: payment_reservation.payment_type == payment_type
            and payment_reservation.partner_type == partner_type
            and payment_reservation.state not in ["posted", "cancel"]
        )
        vals = {
            "payment_type": payment_type,
            "partner_type": partner_type,
            "partner_id": self.partner_id.id,
            "destination_account_id": account.id,
            "payment_method_id": payment_method_id,
            "amount": abs(self.balance) - sum(other_payments.mapped("amount")),
            "ref": _("Reservation {}").format(self.reservation_no),
            "company_id": self.company_id.id,
            "date": fields.Datetime.now().date(),
            "journal_id": journal.id,
            "reservation_id": self.id,
            "state": "draft",
        }
        payment = self.env["account.payment"].sudo().create(vals)
        return payment

    def action_check_in_check_out(self):
        
        """Check in/out Reservation."""
        if self.reservation_type == "individual":
            # fill check in and check out
            if self._context.get("default_check_type") == "in":
                self.date_check_in = datetime.today()
                self.partner_id.sudo().last_room_id = self.reservation_line[
                    -1
                ].room_id.id
                # create and post invoice
                if not self.folio_id.hotel_invoice_id:
                    self.create_post_invoice()
            if self._context.get("default_check_type") == "out":
                # Case when the guest owes the hotel money
                if self.return_insurance == False and self.insurance != 0:
                    raise ValidationError(_('You must return the insurance to the client'))
                if self.balance < 0:
                    raise ValidationError(_('There is an outstanding balance. Please settle all bills before checking out.'))
                elif self.balance > 0:
                    raise ValidationError(_('The hotel owes you a balance. Please contact the front desk for refund processing.'))
                else:
                    checkout = (
                        self.checkout
                        if not self.date_termination
                        else self.date_termination
                    )
                    self.date_check_out = datetime.today()
                    self.create_housekeeping(self.reservation_line.mapped("room_id"))
                    # send rating mail to customer
                    self.rated_partner_id = self.partner_id
                    self.send_rating_mail_customer(self.partner_id)
                    self.reservation_line.mapped("room_id").write(
                        {"is_clean": False, "status": "available"}
                    )
                    self.partner_id.sudo().last_room_id = False
                    if self.date_check_out and self.date_termination and not self.balance:
                        self.state = "finish"
                    # create and post invoice
                    # if not self.hotel_invoice_id:
                    #     self.create_post_invoice()
                    
                    # add day if time checkout excceed hours in setting
                    hour_setting = self.env["hotel.reservation.setting"].search(
                        [("company_id", "=", self.company_id.id)], limit=1
                    )
                    if not self.date_termination:
                        if hour_setting and hour_setting.hours_day:
                            hour, minute = self.get_hour_minute_float(hour_setting.hours_day)
                            if self.rent == "daily" and (
                                self.date_check_out.date() > checkout.date()
                                or (
                                    self.date_check_out.date() == checkout.date()
                                    and self._format_date(str(self.date_check_out)).time()
                                    > time(hour, minute, 0)
                                )
                            ):
                                payments = self.payment_ids.filtered(
                                    lambda payment_reservation: payment_reservation.payment_type
                                    == "inbound"
                                    and payment_reservation.state == "posted"
                                )
                                self.duration += 1
                                self._compute_total_room_rate()
                                if self.folio_id.state != "draft":
                                    self.set_folio_draft()
                                    for room_line in self.folio_id.room_line_ids:
                                        self.update_folio_invoice_qty(room_line)
                            # post and confirm sale and invoice
                            if self.folio_id.state == "draft":
                                self.post_folio_invoice("sale", "posted", payments)
                        # create payment outbound or inbound if the is a balance
                        if self.balance:
                            if self.balance > 0:
                                payment = self.action_payment_create(
                                    "outbound",
                                    "customer",
                                    self.partner_id.with_company(
                                        self.company_id
                                    ).property_account_payable_id,
                                )
                            else:
                                payment = self.action_payment_create(
                                    "inbound",
                                    "customer",
                                    self.partner_id.with_company(
                                        self.company_id
                                    ).property_account_receivable_id,
                                )
                            self.payment_ids += payment




        else:
            # open wizard to choose rooms
            check_type = (
                "in" if self._context.get("default_check_type") == "in" else "out"
            )
            wizard = self.env["hotel.reservation.check.wizard"].create(
                {"reservation_id": self.id, "check_type": check_type}
            )
            context = self._context.copy()
            if self._context.get("default_check_type") == "out":
                lines = self.reservation_line.filtered(
                    lambda line: not line.date_check_out
                    and line.date_check_in
                    and (
                        (
                            line.date_termination
                            and line.date_termination.date() <= datetime.today().date()
                        )
                        or (
                            not line.date_termination
                            and (
                                self.checkout.date() <= datetime.today().date()
                                and not line.date_extension
                            )
                            or (
                                line.date_extension
                                and line.date_extension.date()
                                <= datetime.today().date()
                            )
                        )
                    )
                )
                context.update({"default_reservation_line_ids": lines.ids})
            return {
                "name": _("Check In/Out Reservation"),
                "res_model": "hotel.reservation.check.wizard",
                "view_mode": "form",
                "res_id": wizard.id,
                "type": "ir.actions.act_window",
                "target": "new",
                "context": context,
            }

    def send_rating_mail_customer(self, partner):
        """Send rating mail to customers"""
        template = self.env.ref(
            "hotel_reservation.rating_hotel_reservation_email_template",
            raise_if_not_found=False,
        )
        if template:
            mail_info = {
                "partner_id": partner.id,
                "partner_name": partner.name,
                "lang": partner.lang,
                "reservation_no": self.reservation_no,
            }
            template.sudo().email_to = partner.email
            template.sudo().with_context(mail_info=mail_info).send_mail(
                self.id, force_send=True
            )

    def rating_get_partner_id(self):
        """Get partner who are going to receive mail"""
        res = super(HotelReservation, self).rating_get_partner_id()
        if self.rated_partner_id:
            return self.rated_partner_id
        return res

    def button_reservation_rating(self):
        """OPen view Rating."""
        reservation_rating = self.env["hotel.reservation.rating"].search(
            [("company_id", "=", self.env.company.id)], limit=1
        )
        # Create rating view if the is no rating view
        if not reservation_rating:
            reservation_rating = (
                self.env["hotel.reservation.rating"]
                .sudo()
                .create(
                    {
                        "name": _("Rating %s") % self.env.company.name,
                        "company_id": self.env.company.id,
                    }
                )
            )
        value = {
            "name": reservation_rating.name,
            "view_type": "form",
            "view_mode": "form",
            "res_model": "hotel.reservation.rating",
            "view_id": False,
            "type": "ir.actions.act_window",
            "res_id": reservation_rating.id,
        }
        return value


class HotelReservationLine(models.Model):
    _name = "hotel.reservation.line"
    _description = "Reservation Line"
    _rec_name = "room_id"

    name = fields.Char("Name")
    line_id = fields.Many2one("hotel.reservation")
    room_id = fields.Many2one("hotel.room", string="Room")
    rooms_available_ids = fields.Many2many(
        "hotel.room",
        "hotel_reservation_room_rel",
        compute="_compute_rooms_available",
        store=1,
    )
    categ_id = fields.Many2one("hotel.room.type", "Room Type")
    total_room_rate = fields.Float(
        string="Total Room Rate", compute="_compute_total_room_rate", store=1
    )
    reservation_type = fields.Selection(related="line_id.reservation_type", store=1)
    tenant = fields.Selection(
        string="Tenant",
        selection=[("person", "Person"), ("company", "Company")],
        default="person",
    )
    partner_id = fields.Many2one(
        "res.partner",
        "Person Name",
    )
    partner_company_id = fields.Many2one(
        "res.partner",
        "Company Name",
    )
    adults = fields.Integer(
        "Number Adults",
    )
    children = fields.Integer(
        "Number Children",
    )
    children_ids = fields.Many2many(
        "res.partner",
        "reservation_line_related_children_rel",
        domain="[('is_guest', '=', True)]",
        string="Children",
    )
    adults_ids = fields.Many2many(
        "res.partner",
        "reservation_line_related_adults_rel",
        domain="[('is_guest', '=', True)]",
        string="Adults",
    )
    date_check_in = fields.Datetime(string="Check in", readonly=1)
    date_check_out = fields.Datetime("Check Out", readonly=1)
    duration_check = fields.Integer(
        string="Check Duration", compute="_compute_check_duration", store=1
    )
    peak_days = fields.Integer(string="Peak days", compute="_compute_peak_days")

    peak_price = fields.Float(string="Peak price", compute="_compute_peak_days")
    date_extension = fields.Datetime(string="Extension Date", readonly=1)
    duration_extension = fields.Integer(
        string="Extension Duration",
        compute="_compute_duration_extension_termination",
        store=1,
    )
    change_date = fields.Datetime(string="Change Date")
    display_button_change_room = fields.Boolean(
        string="Display button change room",
        compute="_compute_display_button_change_room",
    )
    date_termination = fields.Datetime(string="Termination Date", readonly=1)
    duration_termination = fields.Integer(
        string="Termination Duration",
        compute="_compute_duration_extension_termination",
        store=1,
    )
    discount_change_room = fields.Float(string="Discount Change Room")
    display_button_service_housekeeping = fields.Boolean(
        string="Display button service housekeeping",
        compute="_compute_display_service_housekeeping",
    )
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

    def get_minimum_price_by_rent(self, rent, room):
        if rent == "daily":
            minimum_price = room.minimum_daily_price
        elif rent == "monthly":
            minimum_price = room.minimum_monthly_price
        else:
            minimum_price = room.minimum_hourly_price
        return minimum_price

    @api.constrains("is_other_price")
    def _check_other_price(self):
        for reservation_line in self:
            if reservation_line.is_other_price:
                if not reservation_line.other_price:
                    raise ValidationError(_("The Price must be more than 0"))
                if reservation_line.line_id.rent == "daily":
                    price = reservation_line.room_id.list_price
                elif reservation_line.line_id.rent == "monthly":
                    price = reservation_line.room_id.monthly_price
                else:
                    price = reservation_line.room_id.hourly_price
                if price >= reservation_line.other_price:
                    raise ValidationError(
                        _("Other price must be greater than Room Price %s") % str(price)
                    )

    @api.constrains("is_minimum_price")
    def _check_minimum_price(self):
        for reservation_line in self:
            if reservation_line.is_minimum_price:
                if not reservation_line.other_price:
                    raise ValidationError(_("Minimum Price must be more than 0"))
                room_minimum_price = reservation_line.get_minimum_price_by_rent(
                    reservation_line.line_id.rent, reservation_line.room_id
                )
                if room_minimum_price > reservation_line.other_price:
                    raise ValidationError(
                        _(
                            "Minimum Price must be equal or greater than Room Minimum Price %s"
                        )
                        % room_minimum_price
                    )

    @api.onchange("tenant")
    def _onchange_tenant(self):
        if self.tenant == "person":
            self.partner_company_id = False
        if self.tenant == "company":
            self.partner_id = False

    @api.constrains("adults", "children")
    def _check_guests(self):
        """Check guests"""
        for reservation_line in self:

            if not reservation_line.room_id:
                raise ValidationError(_("Please Select Rooms For Reservation."))
            # TODO check room capacity
            # if (reservation_line.adults + reservation_line.children) > sum(
            #     reservation_line.mapped("room_id.capacity")
            # ):
            #     raise ValidationError(
            #         _(
            #             "Room Capacity Exceeded \n"
            #             " Please Select Rooms According to"
            #             " Members Accomodation."
            #         )
            #     )

    @api.onchange("children_ids", "adults_ids")
    def _onchange_children_adults(self):
        """Calculate children and aduls"""
        self.children = len(self.children_ids)
        self.adults = len(self.adults_ids)

    @api.onchange("categ_id")
    def on_change_categ(self):
        """
        When you change categ_id it check checkin and checkout are
        filled or not if not then raise warning
        -----------------------------------------------------------
        @param self: object pointer
        """
        if not self.line_id.checkin:
            raise ValidationError(
                _(
                    """Before choosing a room,\n You have to """
                    """select a Check in date or a Check out """
                    """ date in the reservation form."""
                )
            )
        hotel_room_ids = self.env["hotel.room"].search(
            [("room_categ_id", "=", self.categ_id.id), ("is_withheld", "=", False)]
        )
        room_ids = []
        for room in hotel_room_ids:
            assigned = False
            for line in room.room_reservation_line_ids.filtered(
                lambda l: l.status != "cancel"
            ):
                if self.line_id.checkin and line.check_in and self.line_id.checkout:
                    if (
                        self.line_id.checkin <= line.check_in <= self.line_id.checkout
                    ) or (
                        self.line_id.checkin <= line.check_out <= self.line_id.checkout
                    ):
                        assigned = True
                    elif (line.check_in <= self.line_id.checkin <= line.check_out) or (
                        line.check_in <= self.line_id.checkout <= line.check_out
                    ):
                        assigned = True
            for rm_line in room.room_line_ids.filtered(lambda l: l.status != "cancel"):
                if self.line_id.checkin and rm_line.check_in and self.line_id.checkout:
                    if (
                        self.line_id.checkin
                        <= rm_line.check_in
                        <= self.line_id.checkout
                    ) or (
                        self.line_id.checkin
                        <= rm_line.check_out
                        <= self.line_id.checkout
                    ):
                        assigned = True
                    elif (
                        rm_line.check_in <= self.line_id.checkin <= rm_line.check_out
                    ) or (
                        rm_line.check_in <= self.line_id.checkout <= rm_line.check_out
                    ):
                        assigned = True
            if not assigned:
                room_ids.append(room.id)
        domain = {"room_id": [("id", "in", room_ids)]}
        return {"domain": domain}

    def unlink(self):
        """
        Overrides orm unlink method.
        @param self: The object pointer
        @return: True/False.
        """
        hotel_room_reserv_line_obj = self.env["hotel.room.reservation.line"]
        for reservation_line in self:
            room_reservation_line = hotel_room_reserv_line_obj.search(
                [
                    ("room_id", "=", reservation_line.room_id.id),
                    ("reservation_id", "=", reservation_line.line_id.id),
                ]
            )
            if room_reservation_line:
                reservation_line.room_id.write({"isroom": True, "status": "available"})
                room_reservation_line.unlink()
        return super(HotelReservationLine, self).unlink()

    def _compute_display_service_housekeeping(self):
        """display button Service housekeeping"""
        for reservation_line in self:
            reservation_line.display_button_service_housekeeping = False
            if (
                not reservation_line.room_id.is_clean
                and reservation_line.line_id.state == "done"
            ):
                reservation_line.display_button_service_housekeeping = True

    def _compute_display_button_change_room(self):
        """display button chaneg rooms"""
        for reservation_line in self:
            reservation_line.display_button_change_room = False
            if reservation_line.line_id.checkout:
                today = (
                    datetime.today()
                    if reservation_line.line_id.rent == "hours"
                    else datetime.today().date()
                )
                checkout = (
                    reservation_line.line_id.checkout
                    if reservation_line.line_id.rent == "hours"
                    else reservation_line.line_id.checkout.date()
                )
                date_termination = False
                date_extension = False
                if reservation_line.date_termination:
                    date_termination = (
                        reservation_line.date_termination
                        if reservation_line.line_id.rent == "hours"
                        else reservation_line.date_termination.date()
                    )
                if reservation_line.date_extension:
                    date_extension = (
                        reservation_line.date_extension
                        if reservation_line.line_id.rent == "hours"
                        else reservation_line.date_extension.date()
                    )
                if (
                    reservation_line.line_id.state == "done"
                    and not reservation_line.line_id.date_check_out
                    and not reservation_line.date_check_out
                    and (
                        (date_termination and date_termination >= today)
                        or (not reservation_line.date_extension and checkout >= today)
                        or (reservation_line.date_extension and date_extension >= today)
                    )
                ):
                    reservation_line.display_button_change_room = True

    @api.depends(
        "room_id",
        "room_id.list_price",
        "room_id.monthly_price",
        "room_id.hourly_price",
        "line_id",
        "line_id.rent",
    )
    def _compute_total_room_rate(self):
        """Calculate room rate."""
        for reservation_line in self:
            if reservation_line.line_id.rent == "daily":
                reservation_line.total_room_rate = reservation_line.room_id.list_price
            elif reservation_line.line_id.rent == "monthly":
                reservation_line.total_room_rate = (
                    reservation_line.room_id.monthly_price
                )
            else:
                reservation_line.total_room_rate = reservation_line.room_id.hourly_price

    @api.depends(
        "line_id.checkout",
        "line_id",
        "line_id.company_id",
        "line_id.checkin",
        "line_id.is_vip",
        "line_id.adults",
        "line_id.children",
        "children",
        "adults",
    )
    def _compute_rooms_available(self):
        """Calculate avaibility rooms."""
        for reservation_line in self:
            reservation_line.rooms_available_ids = []
            domain_suite = [
                ("room_categ_id.is_vip", "=", False),
                ("company_id", "=", reservation_line.line_id.company_id.id),
            ]
            if reservation_line.line_id.is_vip:
                domain_suite = [
                    ("room_categ_id.is_vip", "=", True),
                    ("company_id", "=", reservation_line.line_id.company_id.id),
                ]
            if reservation_line.line_id.checkout and reservation_line.line_id.checkin:
                # get rooms by dates and capacity
                # TODO check room capacity
                available_rooms = (
                    reservation_line.env["hotel.room"]
                    .search(
                        [
                            ("is_withheld", "=", False),
                            (
                                "id",
                                "not in",
                                reservation_line.line_id.reservation_line.mapped(
                                    "room_id"
                                ).ids,
                            ),
                        ]
                        + domain_suite
                    )
                    .filtered(
                        lambda room: not room.get_status_room_dates(
                            reservation_line.line_id,
                            reservation_line.line_id.checkin,
                            reservation_line.line_id.checkout,
                        )
                        and (
                            (
                                reservation_line.line_id.reservation_type
                                == "individual"
                                # and room.capacity
                                # >= (
                                #     reservation_line.line_id.adults
                                #     + reservation_line.line_id.children
                                # )
                            )
                            or (
                                reservation_line.line_id.reservation_type
                                == "collective"
                                # and room.capacity
                                # >= (reservation_line.adults + reservation_line.children)
                            )
                        )
                    )
                )
                if available_rooms:
                    reservation_line.rooms_available_ids = available_rooms.ids

    @api.depends("date_check_in", "date_check_out", "line_id.rent")
    def _compute_check_duration(self):
        """Calculate check duration."""
        for reservation_line in self:
            reservation_line.duration_check = 0
            if reservation_line.date_check_in and reservation_line.date_check_out:
                reservation_line.duration_check = reservation_line.line_id.get_duration(
                    reservation_line.line_id.rent,
                    reservation_line.date_check_in,
                    reservation_line.date_check_out,
                )

    @api.depends(
        "date_extension", "date_termination", "line_id.rent", "line_id.checkin"
    )
    def _compute_duration_extension_termination(self):
        """Calculate extension and termination duration duration."""
        for reservation_line in self:
            reservation_line.duration_extension = (
                reservation_line.duration_termination
            ) = 0
            # Calculate extension duration
            if reservation_line.line_id.checkin:
                if reservation_line.date_extension:
                    reservation_line.duration_extension = (
                        reservation_line.line_id.get_duration(
                            reservation_line.line_id.rent,
                            reservation_line.line_id.checkin,
                            reservation_line.date_extension,
                        )
                    )
                # Calculate termination duration
                if reservation_line.date_termination:
                    reservation_line.duration_termination = (
                        reservation_line.line_id.get_duration(
                            reservation_line.line_id.rent,
                            reservation_line.line_id.checkin,
                            reservation_line.date_termination,
                        )
                    )

    def get_price_settings(self, categ, company, check_in, check_out):
        """Get setting based on type room ans dates"""
        if check_out and check_in and company and categ:
            return self.env["price.setting"].search(
                [
                    ("room_type_id", "=", categ),
                    ("company_id", "=", company),
                    "&",
                    "|",
                    "&",
                    ("date_to", "<=", check_in.date()),
                    ("date_from", ">=", check_out.date()),
                    ("date_to", ">=", check_in.date()),
                    ("date_from", "<=", check_out.date()),
                ]
            )
        return self.env["price.setting"]

    def calculate_peak_room_days(self, rent, checkin, checkout, date_from, date_to):
        """Calculate peak room days"""
        peak_days = 0
        if checkin.date() >= date_from:
            if checkout.date() >= date_to:
                peak_days += relativedelta(date_to, checkin.date()).days + 1
            elif checkout.date() <= date_to:
                peak_days += relativedelta(checkout.date(), checkin.date()).days + 1
        else:
            if checkout.date() >= date_to:
                peak_days += relativedelta(date_to, date_from).days + 1
            elif checkout.date() <= date_to:
                peak_days += relativedelta(checkout.date(), date_from).days + 1
        if rent == "daily" and checkin.date() != checkout.date():
            peak_days -= 1
        return peak_days

    def calculate_peak_room_price(
        self, rent, room, company, check_in, check_out, duration
    ):
        """Calculate peak room price"""
        peak_by_room_days = 0
        peak_room_price = 0
        if rent == "daily":
            price_unit = room.list_price
        elif rent == "monthly":
            price_unit_month = room.monthly_price
            price_unit = price_unit_month / 30
            if check_out and check_in:
                duration = (check_out - check_in).days
        else:
            price_unit = room.hourly_price
            duration = (check_out - check_in).days + 1
        for setting in self.get_price_settings(
            room.room_categ_id.id, company, check_in, check_out
        ):
            peak_room_days = 0
            peak_room_days += self.calculate_peak_room_days(
                rent, check_in, check_out, setting.date_from, setting.date_to
            )
            peak_by_room_days += self.calculate_peak_room_days(
                rent, check_in, check_out, setting.date_from, setting.date_to
            )
            amount = (
                (setting.amount * price_unit) / 100
                if setting.addition_type == "percentage"
                else setting.amount
            )
            peak_room_price += (amount + price_unit) * peak_room_days
        peak_all_room_price = (
            float(
                (peak_room_price + (price_unit * (duration - peak_by_room_days)))
                / duration
            )
            if duration
            else 0
        )
        if rent == "monthly":
            peak_all_room_price = peak_all_room_price * 30
        return peak_all_room_price

    def _compute_peak_days(self):
        """Calculate peak days and price"""
        for reservation_line in self:
            peak_all_room_days = 0
            peak_all_room_price = 0
            checkout = (
                reservation_line.line_id.checkout
                if not reservation_line.date_extension
                else reservation_line.date_extension
            )
            duration = (
                reservation_line.line_id.duration
                if not reservation_line.date_extension
                else reservation_line.duration_extension
            )
            if reservation_line.date_termination:
                checkout = reservation_line.date_termination
                duration = reservation_line.duration_termination
            if reservation_line.line_id.checkin and reservation_line.line_id.checkout:
                for setting in reservation_line.get_price_settings(
                    reservation_line.room_id.room_categ_id.id,
                    reservation_line.line_id.company_id.id,
                    reservation_line.line_id.checkin,
                    checkout,
                ):
                    # Calculate peak days
                    peak_all_room_days += self.calculate_peak_room_days(
                        reservation_line.line_id.rent,
                        reservation_line.line_id.checkin,
                        checkout,
                        setting.date_from,
                        setting.date_to,
                    )
                # Calculate peak price
                peak_all_room_price += self.calculate_peak_room_price(
                    reservation_line.line_id.rent,
                    reservation_line.room_id,
                    reservation_line.line_id.company_id.id,
                    reservation_line.line_id.checkin,
                    checkout,
                    duration,
                )
            reservation_line.peak_days = peak_all_room_days
            reservation_line.peak_price = (
                peak_all_room_price if peak_all_room_days else 0
            )

    def action_change_room(self):
        """Change Room  Reservation."""
        wizard = self.env["reservation.room.change.wizard"].create(
            {
                "reservation_id": self.line_id.id,
                "reservation_line_id": self.id,
                "old_room_id": self.room_id.id,
                "origin_rent": self.line_id.rent,
            }
        )
        return {
            "name": _("Change Room"),
            "res_model": "reservation.room.change.wizard",
            "view_mode": "form",
            "res_id": wizard.id,
            "type": "ir.actions.act_window",
            "target": "new",
        }

    def create_service_housekeeping(self):
        """Create Cleanliness Service."""
        # if there is housekeeping return it else create a new housekeeping
        # search Cleanliness Service Housekeeping
        housekeeping = (
            self.env["hotel.housekeeping"]
            .sudo()
            .search(
                [
                    ("type", "=", "cleanliness"),
                    ("clean_type", "=", "checkin"),
                    ("room_id", "=", self.room_id.id),
                    ("reservation_id", "=", self.line_id.id),
                ],
                limit=1,
            )
        )
        if not housekeeping:
            # Prepare  Cleanliness Service Housekeeping vals
            vals = {
                "reservation_id": self.line_id.id,
                "type": "cleanliness",
                "clean_type": "checkin",
                "room_id": self.room_id.id,
                "company_id": self.line_id.company_id.id,
                "inspect_date_time": fields.Datetime.now(),
                "categ_id": self.room_id.room_categ_id.id,
            }
            # Search Cleanliness Activity
            activity = (
                self.env["hotel.activity"]
                .sudo()
                .search([("categ_id.type", "=", "cleanliness")], limit=1)
            )
            # Search Clean User
            clean_user = (
                self.env["res.users"]
                .sudo()
                .search(
                    [
                        (
                            "groups_id",
                            "=",
                            self.env.ref("hotel_housekeeping.group_clean_worker").id,
                        )
                    ],
                    limit=1,
                )
            )
            if activity and clean_user:
                # Create Cleanliness Activity
                vals_activity = {
                    "activity_id": activity.id,
                    "housekeeper_id": clean_user.id,
                    "clean_start_time": fields.Datetime.now(),
                    "clean_end_time": fields.Datetime.now() + timedelta(hours=1),
                    "today_date": datetime.today().date(),
                }
                vals.update({"activity_line_ids": [(0, 0, vals_activity)]})

            # Create Cleanliness Service Housekeeping
            housekeeping = self.env["hotel.housekeeping"].sudo().create(vals)
            housekeeping._onchange_room()
        return {
            "name": _("Housekeeping Cleanliness Service"),
            "res_model": "hotel.housekeeping",
            "view_mode": "form",
            "type": "ir.actions.act_window",
            "res_id": housekeeping.id,
            "target": "current",
        }


class HotelRoomReservationLine(models.Model):
    _name = "hotel.room.reservation.line"
    _description = "Hotel Room Reservation"
    _rec_name = "room_id"

    room_id = fields.Many2one(
        "hotel.room", string="Room id", domain="[('is_withheld','=', False)]"
    )
    check_in = fields.Datetime("Check In Date", required=True)
    check_out = fields.Datetime("Check Out Date", required=True)
    state = fields.Selection(
        [("assigned", "Assigned"), ("unassigned", "Unassigned")], "Room Status"
    )
    reservation_id = fields.Many2one("hotel.reservation", "Reservation")
    status = fields.Selection(string="state", related="reservation_id.state")
    reservation_line_id = fields.Many2one("hotel.reservation.line", "Reservation line")


class HotelRoomReservationChange(models.Model):
    _name = "reservation.room.change.history"
    _description = "Reservation Room Change History"
    _rec_name = "room_id"

    change_date = fields.Datetime(string="Change Date")
    reservation_date = fields.Datetime(string="Reservation Date")
    old_room_id = fields.Many2one("hotel.room", string="Old Room")

    room_id = fields.Many2one(
        "hotel.room", string="Room", domain="[('is_withheld','=', False)]"
    )
    reservation_id = fields.Many2one("hotel.reservation", "Reservation")
    reservation_line_id = fields.Many2one("hotel.reservation.line", "Reservation line")
    is_no_calculated = fields.Boolean(string="Not calculated")
    discount = fields.Float(string="Discount")
    discount_type = fields.Selection(
        string="Discount Type",
        selection=[
            ("no_discount", "No Discount"),
            ("percentage", "Percentage"),
            ("amount", "amount"),
        ],
    )
    insurance = fields.Float(string="Insurance")
    old_other_price = fields.Float(string="Old Other price")
    other_price = fields.Float(string="Other Price")


class FolioRoomLine(models.Model):
    _inherit = "folio.room.line"

    reservation_line_id = fields.Many2one("hotel.reservation.line", "Reservation Line")


class HotelReservationHospitality(models.Model):
    _name = "hotel.reservation.hospitality"
    _description = "Reservation Hospitality"

    discount_type = fields.Selection(
        string="Discount Type",
        selection=[
            ("no_discount", "No Discount"),
            ("percentage", "Percentage"),
            ("amount", "Amount"),
        ],
        default="no_discount",
    )
    discount = fields.Float(
        string="Discount ",
    )
    company_id = fields.Many2one(
        "res.company", string="Company", default=lambda self: self.env.company
    )
    active = fields.Boolean(default=True)

    @api.constrains("company_id")
    def _check_company(self):
        """Check company."""
        for reservation_hospitality in self:
            if self.search(
                [
                    ("company_id", "=", reservation_hospitality.company_id.id),
                    ("id", "!=", reservation_hospitality.id),
                ]
            ):
                raise ValidationError(
                    _("You should add one reservation hospitality for each company")
                )


class HotelReservationSetting(models.Model):

    _name = "hotel.reservation.setting"
    _description = "Reservation Setting"

    name = fields.Char(string="Name", translate=1, required=1, default="Setting")
    hours_day = fields.Float(string="Hour that is exceeded is counted as another day")
    company_id = fields.Many2one(
        "res.company", string="Company", default=lambda self: self.env.company
    )
    active = fields.Boolean(default=True)



# # See LICENSE file for full copyright and licensing details.

# import math
# from datetime import datetime, time, timedelta

# import pytz
# from dateutil.relativedelta import relativedelta
# from ummalqura.hijri_date import HijriDate

# from odoo import _, api, fields, models
# from odoo.exceptions import ValidationError
# from odoo.osv import expression
# # related_invoice_ids

# class HotelReservation(models.Model):
#     _name = "hotel.reservation"
#     _rec_name = "reservation_no"
#     _description = "Reservation"
#     _order = "reservation_no desc"
#     _inherit = ["mail.thread", "mail.activity.mixin", "rating.mixin"]

#     related_invoice_ids = fields.Many2many('account.move', compute='_compute_related_invoices', string='Related Invoices')

#     @api.depends('folio_id.invoice_ids')
#     def _compute_related_invoices(self):
#         for record in self:
#             # Directly linking the invoices associated with the folio of this reservation
#             record.related_invoice_ids = record.folio_id.invoice_ids
            
            
#     def _compute_folio_count(self):
#         for res in self:
#             res.update({"no_of_folio": len(res.folio_id.ids)})

#     reservation_no = fields.Char("Reservation No", readonly=True)
#     date_order = fields.Datetime(
#         "Date Ordered",
#         readonly=True,
#         required=True,
#         index=True,
#         default=lambda self: fields.Datetime.now(),
#     )

#     company_id = fields.Many2one(
#         "res.company",
#         "Hotel",
#         readonly=True,
#         index=True,
#         required=True,
#         states={"draft": [("readonly", False)]},
#         default=lambda self: self.env.company,
#     )
#     partner_id = fields.Many2one(
#         "res.partner",
#         "Guest Name",
#         readonly=True,
#         index=True,
#         required=True,
#         domain="[('is_guest', '=', True)]",
#         states={"draft": [("readonly", False)]},
#     )
#     partner_invoice_id = fields.Many2one(
#         "res.partner",
#         "Invoice Address",
#         readonly=True,
#         states={"draft": [("readonly", False)]},
#         help="Invoice address for " "current reservation.",
#     )
#     partner_order_id = fields.Many2one(
#         "res.partner",
#         "Ordering Contact",
#         readonly=True,
#         states={"draft": [("readonly", False)]},
#         help="The name and address of the "
#         "contact that requested the order "
#         "or quotation.",
#     )
#     partner_shipping_id = fields.Many2one(
#         "res.partner",
#         "Delivery Address",
#         readonly=True,
#         states={"draft": [("readonly", False)]},
#         help="Delivery address" "for current reservation. ",
#     )
#     checkin = fields.Datetime(
#         "Expected-Date-Arrival",
#         required=True,
#         readonly=True,
#         states={"draft": [("readonly", False)]},
#         tracking=1,
#         default=lambda self: fields.Datetime.now(),
#     )
#     checkout = fields.Datetime(
#         "Expected-Date-Departure",
#         required=True,
#         readonly=True,
#         states={"draft": [("readonly", False)]},
#         tracking=1,
#     )
#     adults = fields.Integer(
#         "Number Adults",
#         readonly=True,
#         states={"draft": [("readonly", False)]},
#         help="List of adults there in guest list. ",
#     )
#     children = fields.Integer(
#         "Number Children",
#         readonly=True,
#         states={"draft": [("readonly", False)]},
#         help="Number of children there in guest list.",
#     )
#     reservation_line = fields.One2many(
#         "hotel.reservation.line",
#         "line_id",
#         string="Reservation Line",
#         help="Hotel room reservation details.",
#         readonly=True,
#         states={"draft": [("readonly", False)]},
#     )
#     state = fields.Selection(
#         [
#             ("draft", "Draft"),
#             ("confirm", "Pre-booking"),
#             ("done", "Done"),
#             ("finish", "Finished"),
#             ("cancel", "Cancel"),
#         ],
#         "State",
#         readonly=True,
#         default="draft",
#         tracking=1,
#     )
#     folio_id = fields.Many2many(
#         "hotel.folio",
#         "hotel_folio_reservation_rel",
#         "order_id",
#         "invoice_id",
#         string="Folio",
#         copy=False,
#     )
#     hotel_invoice_id = fields.Many2one(related="folio_id.hotel_invoice_id", store=1)
#     no_of_folio = fields.Integer("No. Folio", compute="_compute_folio_count")
#     source_id = fields.Many2one(
#         "hotel.reservation.source",
#         string="Source Reservation",
#         readonly=True,
#         states={"draft": [("readonly", False)]},
#     )
#     rent = fields.Selection(
#         string="Rent Type",
#         selection=[("daily", "Daily"), ("monthly", "Monthly"), ("hours", "Hours")],
#         default="daily",
#         readonly=True,
#         states={"draft": [("readonly", False)]},
#     )
#     source_number = fields.Char(
#         string="Reservation source number",
#         readonly=True,
#         states={"draft": [("readonly", False)]},
#     )
#     duration = fields.Integer(
#         string="Duration",
#         readonly=True,
#         states={"draft": [("readonly", False)]},
#         default=1,
#     )
#     reason_id = fields.Many2one(
#         "reservation.visit.reason",
#         string="Visit Reason",
#         readonly=True,
#         states={"draft": [("readonly", False)]},
#     )
#     note = fields.Text(
#         string="Notes",
#         readonly=True,
#         states={"draft": [("readonly", False)]},
#     )
#     reservation_type = fields.Selection(
#         string="Reservation Type",
#         selection=[("individual", "Individual"), ("collective", "Collective")],
#         default="individual",
#         readonly=True,
#         states={"draft": [("readonly", False)]},
#     )
#     room_rate = fields.Float(
#         string="Rooms Rate", compute="_compute_total_room_rate", store=1
#     )
#     total_room_rate = fields.Float(
#         string="Untaxed Total Rate", compute="_compute_total_room_rate", store=1
#     )
#     children_ids = fields.Many2many(
#         "res.partner",
#         "reservation_related_children_rel",
#         string="Children",
#         readonly=True,
#         states={"draft": [("readonly", False)]},
#     )
#     adults_ids = fields.Many2many(
#         "res.partner",
#         "reservation_related_adults_rel",
#         string="Adults",
#         readonly=True,
#         states={"draft": [("readonly", False)]},
#     )
#     discount_type = fields.Selection(
#         string="Discount Type",
#         selection=[
#             ("no_discount", "No Discount"),
#             ("percentage", "Percentage"),
#             ("amount", "amount"),
#         ],
#         default="no_discount",
#         readonly=True,
#         states={"draft": [("readonly", False)]},
#     )
#     discount_percentage = fields.Float(
#         string="Percentage",
#         readonly=True,
#         states={"draft": [("readonly", False)]},
#     )
#     discount = fields.Float(
#         string="Discount",
#         readonly=True,
#         states={"draft": [("readonly", False)]},
#     )
#     insurance = fields.Float(
#         string="Insurance",
#         readonly=True,
#         states={"draft": [("readonly", False)], "confirm": [("readonly", False)]},
#     )
#     insurance_change_room = fields.Float(string="Insurance Change Room")
#     discount_change_room = fields.Float(
#         string="Discount Change Room", compute="_compute_total_room_rate", store=1
#     )
#     taxes_amount = fields.Float(
#         string="Taxes ", compute="_compute_total_room_rate", store=1
#     )
#     taxed_total_rate = fields.Float(
#         string="Taxed Total Rate", compute="_compute_total_room_rate", store=1
#     )
#     total_cost = fields.Float(
#         string="Total Cost", compute="_compute_total_room_rate", store=1
#     )
#     final_cost = fields.Float(
#         string="Final cost",
#         compute="_compute_total_room_rate",
#         store=1,
#         tracking=1,
#     )
#     payments_count = fields.Float(
#         string="Payments", compute="_compute_payments", store=1
#     )
#     payment_totals = fields.Text(
#         string="Payment Totals", compute="_compute_payment_totals"
#     )
#     balance = fields.Float(string="Balance", compute="_compute_payments", store=1)
#     is_send_shomoos = fields.Boolean(string="Send to Shomoos Service")
#     is_send_tourism = fields.Boolean(string="Send to Tourism Platform Service")
#     service_amount = fields.Float(
#         string="Services", related="folio_id.service_amount", store=1
#     )
#     service_tax = fields.Float(
#         string="Services Tax", related="folio_id.service_tax", store=1
#     )
#     is_returnable = fields.Boolean(
#         string="Returnable",
#         readonly=True,
#         states={"draft": [("readonly", False)]},
#         default=True,
#     )
#     returnable_percentage = fields.Float(
#         string="Percentage ",
#         readonly=True,
#         states={"draft": [("readonly", False)]},
#     )
#     returnable_amount = fields.Float(
#         string="Returned Amount ",
#         compute="_compute_total_room_rate",
#         store=1,
#     )
#     is_returnable_reservation = fields.Boolean(
#         string="Returnable Reservation", copy=False
#     )
#     date_check_in = fields.Datetime(string="Check in", readonly=1)
#     date_check_out = fields.Datetime("Check Out", readonly=1)
#     duration_check = fields.Integer(
#         string="Check Duration", compute="_compute_check_duration", store=1
#     )
#     display_button_terminate_reservation = fields.Boolean(
#         string="Display button terminate reservation",
#         compute="_compute_display_button_reservation",
#     )
#     display_button_check_in_reservation = fields.Boolean(
#         string="Display button check in reservation",
#         compute="_compute_display_button_reservation",
#     )
#     display_button_check_out_reservation = fields.Boolean(
#         string="Display button check out reservation",
#         compute="_compute_display_button_reservation",
#     )
#     display_button_extend_reservation = fields.Boolean(
#         string="Display button extend reservation",
#         compute="_compute_display_button_reservation",
#     )
#     display_button_cancel = fields.Boolean(
#         string="Display button cancel reservation",
#         compute="_compute_display_button_reservation",
#     )
#     display_button_returned_reservation = fields.Boolean(
#         string="Display button returned reservation",
#         compute="_compute_display_button_reservation",
#     )
#     is_vip = fields.Boolean(
#         string="VIPS",
#         readonly=True,
#         states={"draft": [("readonly", False)]},
#     )
#     history_room_ids = fields.One2many(
#         "reservation.room.change.history", "reservation_id", string="History Rooms"
#     )
#     reason_cancel = fields.Text(string="Cancel Reason", readonly=1)
#     rated_partner_id = fields.Many2one("res.partner", string="Rated Partner")
#     is_checked_in = fields.Boolean(
#         string="Is Checked In", compute="_compute_is_checked_in", store=True
#     )
#     is_checked_out = fields.Boolean(
#         string="Is Checked Out", compute="_compute_is_checked_out", store=True
#     )
#     date_termination = fields.Datetime(string="Termination Date", readonly=1)
#     mobile = fields.Char(related="partner_id.mobile", store=1)
#     identification_id = fields.Char(related="partner_id.identification_id", store=1)
#     visa_number = fields.Char(related="partner_id.visa_number", store=1)
#     card_number = fields.Char(related="partner_id.card_number", store=1)
#     residence_number = fields.Char(related="partner_id.residence_number", store=1)
#     passport_id = fields.Char(related="partner_id.passport_id", store=1)
#     is_hospitality = fields.Boolean(
#         string="Hospitality",
#         readonly=True,
#         states={"draft": [("readonly", False)]},
#     )
#     payment_ids = fields.One2many(
#         "account.payment", "reservation_id", string="Payments", index=True
#     )
#     rooms = fields.Char(string="Rooms", compute="_compute_rooms")
#     taxes_info = fields.Text(string="Taxes details")

#     def _format_date(self, naive_dt):
#         """Convert datetime from utc to tz"""
#         naive = datetime.strptime(naive_dt[:19], "%Y-%m-%d %H:%M:%S")
#         tz_name = self.env.user.tz
#         tz = pytz.timezone(tz_name) if tz_name else pytz.utc
#         ran = pytz.utc.localize(naive).astimezone(tz)
#         date = datetime.strptime(str(ran)[:19], "%Y-%m-%d %H:%M:%S")
#         return date

#     def get_hour_minute_float(self, float_val):
#         """Get hour and minute from float"""
#         factor = float_val < 0 and -1 or 1
#         val = abs(float_val)
#         hour, minute = (factor * int(math.floor(val)), int(round((val % 1) * 60)))
#         if minute == 60:
#             hour = hour + 1
#             minute = 0
#         return hour, minute

#     def _compute_rooms(self):
#         """Get rooms numbers"""
#         for reservation in self:
#             rooms = set(
#                 reservation.reservation_line.mapped("room_id")
#                 + reservation.history_room_ids.filtered(
#                     lambda history: not history.is_no_calculated
#                     and history.reservation_date.date() != history.change_date.date()
#                 ).mapped("room_id")
#                 + reservation.history_room_ids.filtered(
#                     lambda history: not history.is_no_calculated
#                     and history.reservation_date.date() != history.change_date.date()
#                 ).mapped("old_room_id")
#             )
#             reservation.rooms = ", ".join(room.name for room in rooms)

#     @api.depends("date_check_in", "reservation_line.date_check_in")
#     def _compute_is_checked_in(self):
#         """Calculate Check Duration."""
#         for reservation in self:
#             reservation.is_checked_in = False
#             if (
#                 reservation.reservation_type == "individual"
#                 and reservation.date_check_in
#             ) or (
#                 reservation.reservation_type == "collective"
#                 and all(reservation.mapped("reservation_line.date_check_in"))
#             ):
#                 reservation.is_checked_in = True

#     @api.depends("date_check_out", "reservation_line.date_check_out")
#     def _compute_is_checked_out(self):
#         """Calculate Check Duration."""
#         for reservation in self:
#             reservation.is_checked_out = False
#             if (
#                 reservation.reservation_type == "individual"
#                 and reservation.date_check_out
#             ) or (
#                 reservation.reservation_type == "collective"
#                 and all(reservation.mapped("reservation_line.date_check_out"))
#             ):
#                 reservation.is_checked_out = True

#     def unlink(self):
#         """
#         Overrides orm unlink method.
#         @param self: The object pointer
#         @return: True/False.
#         """
#         lines_of_moves_to_post = self.filtered(
#             lambda reserv_rec: reserv_rec.state != "draft"
#         )
#         if lines_of_moves_to_post:
#             raise ValidationError(
#                 _("Sorry, you can only delete the reservation when it's draft!")
#             )
#         quick_reservation_ids = self.env["quick.room.reservation"].search(
#             [("reservation_id", "=", self.id)]
#         )
#         quick_reservation_ids.unlink()
#         return super(HotelReservation, self).unlink()

#     def copy(self):
#         ctx = dict(self._context) or {}
#         ctx.update({"duplicate": True})
#         return super(HotelReservation, self.with_context(ctx)).copy()

#     @api.constrains("reservation_line", "adults", "children")
#     def _check_reservation_rooms(self):
#         """
#         This method is used to validate the reservation_line.
#         -----------------------------------------------------
#         @param self: object pointer
#         @return: raise a warning depending on the validation
#         """
#         dict(self._context) or {}
#         for reservation in self:
#             # TODO check room capacity

#             # if not ctx.get("duplicate"):
#             #     if reservation.reservation_line.mapped("room_id") and (
#             #         reservation.adults + reservation.children
#             #     ) > sum(reservation.reservation_line.mapped("room_id.capacity")):
#             #         raise ValidationError(
#             #             _(
#             #                 "Room Capacity Exceeded \n"
#             #                 " Please Select Rooms According to"
#             #                 " Members Accomodation."
#             #             )
#             #         )
#             if (
#                 reservation.reservation_type == "individual"
#                 and len(reservation.adults_ids) != reservation.adults
#             ):
#                 raise ValidationError(
#                     _(
#                         "The number of adults must correspond to the number of selected adults."
#                     )
#                 )

#     @api.constrains("checkin", "checkout")
#     def check_in_out_dates(self):
#         """
#         When date_order is less then check-in date or
#         Checkout date should be greater than the check-in date.
#         """
#         if self.checkout and self.checkin:
#             if self.checkin.date() < self.date_order.date():
#                 raise ValidationError(
#                     _(
#                         """Check-in date should be greater than """
#                         """the current date."""
#                     )
#                 )
#             if self.checkout < self.checkin:
#                 raise ValidationError(
#                     _("""Check-out date should be greater """ """than Check-in date.""")
#                 )

#     @api.onchange("reservation_line")
#     def _onchange_reservation_line(self):
#         for reservation in self:
#             if (
#                 reservation.reservation_type == "individual"
#                 and len(reservation.reservation_line) > 1
#             ):
#                 raise ValidationError(
#                     _("You cannot add more than one room for individual reservation .")
#                 )

#     @api.onchange("discount_type")
#     def _onchange_discount_type(self):
#         """Change discount value based on hospitality."""
#         if self.discount_type:
#             self.discount_percentage = 0
#             self.discount = 0
#             # change discount based on type Hospitality
#             if self.is_hospitality:
#                 reservation_hospitality = self.env[
#                     "hotel.reservation.hospitality"
#                 ].search([("company_id", "=", self.company_id.id)], limit=1)
#                 if reservation_hospitality.discount_type == "amount":
#                     self.discount = reservation_hospitality.discount
#                 else:
#                     self.discount_percentage = reservation_hospitality.discount

#     @api.onchange("is_hospitality")
#     def _onchange_hospitality(self):
#         """Change discount value when check hospitality."""
#         # change discount type based on type Hospitality
#         if self.is_hospitality:
#             reservation_hospitality = self.env["hotel.reservation.hospitality"].search(
#                 [("company_id", "=", self.company_id.id)], limit=1
#             )
#             if reservation_hospitality:
#                 self.discount_type = reservation_hospitality.discount_type
#         else:
#             self.discount_type = "no_discount"
#             self.discount_percentage = 0
#             self.discount = 0

#     @api.onchange("is_returnable")
#     def _onchange_is_returnable(self):
#         """Clear returnable percentage."""
#         if not self.is_returnable:
#             self.returnable_percentage = 0

#     @api.onchange("partner_id")
#     def _onchange_partner_id(self):
#         """
#         When you change partner_id it will update the partner_invoice_id,
#         partner_shipping_id  of the hotel reservation as well
#         ---------------------------------------------------------------------
#         @param self: object pointer
#         """
#         if not self.partner_id:
#             self.update(
#                 {
#                     "partner_invoice_id": False,
#                     "partner_shipping_id": False,
#                     "partner_order_id": False,
#                 }
#             )
#         else:
#             addr = self.partner_id.address_get(["delivery", "invoice", "contact"])
#             self.update(
#                 {
#                     "partner_invoice_id": addr["invoice"],
#                     "partner_shipping_id": addr["delivery"],
#                     "partner_order_id": addr["contact"],
#                 }
#             )

#     def _create_quick_reservation(self):
#         """Create quick reservation when create new reservation
#         or add new line in reservation created."""
#         for line in self.reservation_line:
#             domain = [
#                 ("reservation_id", "=", self.id),
#                 ("room_id", "=", line.room_id.id),
#             ]
#             # Get the right value of guest to check if quick reservation created or no.
#             # Check if the thype of reservation is individual
#             # to get the value of guest from individual.
#             if self.reservation_type == "individual":
#                 domain = expression.AND(
#                     [domain, [("partner_id", "=", self.partner_id.id)]]
#                 )
#             else:
#                 # If the type of reservation is collective we will check if this reservation
#                 # for company or person to get the right value of guest.
#                 if line.tenant == "person":
#                     domain = expression.AND(
#                         [domain, [("partner_id", "=", line.partner_id.id)]]
#                     )
#                 else:
#                     domain = expression.AND(
#                         [domain, [("partner_id", "=", line.partner_company_id.id)]]
#                     )
#             quick_reservation_ids = self.env["quick.room.reservation"].search(domain)
#             if not quick_reservation_ids:
#                 val = {
#                     "reservation_id": self.id,
#                     "partner_id": self.partner_id.id,
#                     "room_id": line.room_id.id,
#                     "check_in": self.checkin,
#                     "check_out": self.checkout,
#                     "source_id": self.source_id.id,
#                     "source_number": self.source_number,
#                     "is_returnable": self.is_returnable,
#                     "returnable_percentage": self.returnable_percentage,
#                     "company_id": self.company_id.id,
#                     "partner_invoice_id": self.partner_invoice_id.id,
#                     "partner_order_id": self.partner_order_id.id,
#                     "partner_shipping_id": self.partner_shipping_id.id,
#                     "reason_id": self.reason_id.id,
#                     "adults": self.adults,
#                 }
#                 if self.reservation_type == "collective":
#                     if line.tenant == "person":
#                         val.update({"partner_id": line.partner_id.id})
#                     else:
#                         val.update({"partner_id": line.partner_company_id.id})
#                 self.env["quick.room.reservation"].create(val)

#     def create_housekeeping(self, rooms):
#         for room in rooms:
#             vals = {
#                 "reservation_id": self.id,
#                 "categ_id": room.room_categ_id.id,
#                 "type": "cleanliness",
#                 "clean_type": "checkout",
#                 "room_id": room.id,
#                 "company_id": self.company_id.id,
#                 "inspect_date_time": fields.Datetime.now(),
#             }
#             activity = (
#                 self.env["hotel.activity"]
#                 .sudo()
#                 .search([("categ_id.type", "=", "cleanliness")], limit=1)
#             )
#             clean_user = (
#                 self.env["res.users"]
#                 .sudo()
#                 .search(
#                     [
#                         (
#                             "groups_id",
#                             "=",
#                             self.env.ref("hotel_housekeeping.group_clean_worker").id,
#                         )
#                     ],
#                     limit=1,
#                 )
#             )
#             if activity and clean_user:
#                 clean_user = (
#                     self.env["res.users"]
#                     .sudo()
#                     .search(
#                         [
#                             (
#                                 "groups_id",
#                                 "=",
#                                 self.env.ref(
#                                     "hotel_housekeeping.group_clean_worker"
#                                 ).id,
#                             )
#                         ],
#                         limit=1,
#                     )
#                 )
#                 vals_activity = {
#                     "activity_id": activity.id,
#                     "housekeeper_id": clean_user.id,
#                     "clean_start_time": fields.Datetime.now(),
#                     "clean_end_time": fields.Datetime.now() + timedelta(hours=1),
#                     "today_date": datetime.today().date(),
#                 }
#                 vals.update({"activity_line_ids": [(0, 0, vals_activity)]})
#             housekeeping = self.env["hotel.housekeeping"].sudo().create(vals)
#             housekeeping._onchange_room()

#     @api.model
#     def create(self, vals):
#         """
#         Overrides orm create method.
#         @param self: The object pointer
#         @param vals: dictionary of fields value.
#         """
#         reservation = super(HotelReservation, self).create(vals)
#         if reservation:
#             reservation.reservation_no = self.env["ir.sequence"].next_by_code(
#                 "hotel.reservation"
#             )
#             reservation._create_quick_reservation()
#             if len(reservation.reservation_line):
#                 reservation.partner_id.last_room_id = reservation.reservation_line[
#                     0
#                 ].room_id.id
#         return reservation

#     def write(self, vals):
#         # Do not allow changing the company_id when account_move_line already exist
#         reservation = super(HotelReservation, self).write(vals)
#         if (
#             vals.get("checkin", False)
#             or vals.get("checkout", False)
#             or vals.get("reservation_line", False)
#         ):
#             self._create_quick_reservation()
#             if len(self.reservation_line):
#                 self.partner_id.last_room_id = self.reservation_line[0].room_id.id
#         return reservation

#     def check_overlap(self, date1, date2):
#         delta = date2 - date1
#         return {date1 + timedelta(days=i) for i in range(delta.days + 1)}

#     def print_invoice(self):
#         return self.env.ref("account.account_invoices_without_payment").report_action(
#             self.hotel_invoice_id
#         )

#     def confirmed_reservation(self):
#         """
#         This method create a new record set for hotel room reservation line
#         -------------------------------------------------------------------
#         @param self: The object pointer
#         @return: new record set for hotel room reservation line.
#         """
#         reservation_line_obj = self.env["hotel.room.reservation.line"]
#         vals = {}
#         for reservation in self:
#             if not len(reservation.reservation_line):
#                 raise ValidationError(_("Please Select Rooms For Reservation."))
#             reserv_checkin = reservation.checkin
#             reserv_checkout = reservation.checkout
#             room_bool = False
#             # Check availability of rooms
#             for reservation_line in reservation.reservation_line:
#                 if reservation_line.room_id.room_reservation_line_ids:
#                     for (
#                         reserv
#                     ) in reservation_line.room_id.room_reservation_line_ids.search(
#                         [
#                             ("status", "in", ("confirm", "done")),
#                             ("room_id", "=", reservation_line.room_id.id),
#                         ]
#                     ):
#                         if (
#                             not reserv.reservation_id.date_check_out
#                             and reserv.reservation_id.reservation_type == "individual"
#                         ) or (
#                             not reserv.reservation_line_id.date_check_out
#                             and reserv.reservation_line_id.room_id
#                             == reservation_line.room_id
#                             and reservation_line.line_id.reservation_type
#                             == "collective"
#                         ):
#                             check_in = reserv.check_in
#                             check_out = reserv.check_out
#                             if check_in <= reserv_checkin <= check_out:
#                                 room_bool = True
#                             if check_in <= reserv_checkout <= check_out:
#                                 room_bool = True
#                             if (
#                                 reserv_checkin <= check_in
#                                 and reserv_checkout >= check_out
#                             ):
#                                 room_bool = True
#                             r_checkin = (reservation.checkin).date()
#                             r_checkout = (reservation.checkout).date()
#                             check_intm = (reserv.check_in).date()
#                             check_outtm = (reserv.check_out).date()
#                             range1 = [r_checkin, r_checkout]
#                             range2 = [check_intm, check_outtm]
#                             overlap_dates = self.check_overlap(
#                                 *range1
#                             ) & self.check_overlap(*range2)
#                         if room_bool:
#                             raise ValidationError(
#                                 _(
#                                     "Room %s cannot be reserved because"
#                                     " it is occupy on these dates %s"
#                                 )
#                                 % (
#                                     reservation_line.room_id.name,
#                                     [
#                                         str(date_overlap)
#                                         for date_overlap in overlap_dates
#                                     ],
#                                 )
#                             )
#                         else:
#                             self.state = "confirm"
#                             vals = {
#                                 "room_id": reservation_line.room_id.id,
#                                 "check_in": reservation.checkin,
#                                 "check_out": reservation.checkout,
#                                 "state": "assigned",
#                                 "reservation_id": reservation.id,
#                                 "reservation_line_id": reservation_line.id,
#                             }
#                             reservation_line.room_id.write(
#                                 {"isroom": False, "status": "occupied"}
#                             )
#                     else:
#                         self.state = "confirm"
#                         vals = {
#                             "room_id": reservation_line.room_id.id,
#                             "check_in": reservation.checkin,
#                             "check_out": reservation.checkout,
#                             "state": "assigned",
#                             "reservation_id": reservation.id,
#                             "reservation_line_id": reservation_line.id,
#                         }
#                         reservation_line.room_id.write(
#                             {"isroom": False, "status": "occupied"}
#                         )
#                 else:
#                     self.state = "confirm"
#                     vals = {
#                         "room_id": reservation_line.room_id.id,
#                         "check_in": reservation.checkin,
#                         "check_out": reservation.checkout,
#                         "state": "assigned",
#                         "reservation_id": reservation.id,
#                         "reservation_line_id": reservation_line.id,
#                     }
#                     reservation_line.room_id.write(
#                         {"isroom": False, "status": "occupied"}
#                     )
#                 reservation_line_obj.create(vals)
#         return True

#     def cancel_reservation(self):
#         """
#         This method cancel record set for hotel room reservation line
#         ------------------------------------------------------------------
#         @param self: The object pointer
#         @return: cancel record set for hotel room reservation line.
#         """
#         wizard = self.env["hotel.reservation.cancel.wizard"].create(
#             {"reservation_id": self.id}
#         )
#         return {
#             "name": _("Cancel Reason"),
#             "res_model": "hotel.reservation.cancel.wizard",
#             "view_mode": "form",
#             "res_id": wizard.id,
#             "type": "ir.actions.act_window",
#             "target": "new",
#         }

#     def set_to_draft_reservation(self):
#         self.update({"state": "draft"})

#     def action_send_reservation_mail(self):
#         """
#         This function opens a window to compose an email,
#         template message loaded by default.
#         @param self: object pointer
#         """
#         self.ensure_one(), "This is for a single id at a time."
#         template_id = self.env.ref(
#             "hotel_reservation.email_template_hotel_reservation"
#         ).id
#         compose_form_id = self.env.ref("mail.email_compose_message_wizard_form").id
#         ctx = {
#             "default_model": "hotel.reservation",
#             "default_res_id": self.id,
#             "default_use_template": bool(template_id),
#             "default_template_id": template_id,
#             "default_composition_mode": "comment",
#             "force_send": True,
#             "mark_so_as_sent": True,
#         }
#         return {
#             "type": "ir.actions.act_window",
#             "view_mode": "form",
#             "res_model": "mail.compose.message",
#             "views": [(compose_form_id, "form")],
#             "view_id": compose_form_id,
#             "target": "new",
#             "context": ctx,
#             "force_send": True,
#         }

#     @api.model
#     def reservation_reminder_24hrs(self):
#         """
#         This method is for scheduler
#         every 1day scheduler will call this method to
#         find all tomorrow's reservations.
#         ----------------------------------------------
#         @param self: The object pointer
#         @return: send a mail
#         """
#         now_date = fields.Date.today()
#         template_id = self.env.ref(
#             "hotel_reservation.mail_template_reservation_reminder_24hrs"
#         )
#         for reserv_rec in self:
#             checkin_date = reserv_rec.checkin
#             difference = relativedelta(now_date, checkin_date)
#             if (
#                 difference.days == -1
#                 and reserv_rec.partner_id.email
#                 and reserv_rec.state == "confirm"
#             ):
#                 template_id.send_mail(reserv_rec.id, force_send=True)
#         return True

#     def set_folio_draft(self):
#         """Update folio and invoice state to draft"""
#         # Update folio state to draft
#         if self.folio_id.state == "sale":
#             self.folio_id.action_folio_cancel()
#             self.folio_id.order_id.action_draft()
#             # Update invoice state to draft
#             if (
#                 self.folio_id.hotel_invoice_id
#                 and self.folio_id.hotel_invoice_id.state != "draft"
#             ):
#                 self.folio_id.hotel_invoice_id.button_draft()

#     def post_folio_invoice(self, folio_state, invoice_state, payments):
#         """post and confirm  folio and invoice"""
#         # post invoice
#         if self.folio_id.hotel_invoice_id:
#             self.folio_id.hotel_invoice_id.with_context(
#                 check_move_validity=False
#             )._recompute_tax_lines()
#             self.folio_id.hotel_invoice_id.with_context(
#                 check_move_validity=False
#             )._onchange_invoice_line_ids()
#             if invoice_state == "posted":
#                 self.folio_id.hotel_invoice_id.action_post()
#                 # relate payment to invoice
#                 for line_id in payments.mapped("line_ids").filtered(
#                     lambda line: line.account_internal_type in ("receivable", "payable")
#                     and not line.reconciled
#                 ):
#                     self.folio_id.hotel_invoice_id.js_assign_outstanding_line(
#                         line_id.id
#                     )
#         # confirm  folio
#         if folio_state == "sale":
#             self.folio_id.action_confirm()

#     def update_room_reservation_line(self, reservation_line, room, checkout):
#         """Update Rooms reservation lines"""
#         room_reservation_line = room.room_reservation_line_ids.filtered(
#             lambda line: line.reservation_line_id.id == reservation_line.id
#         )
#         room_line_id = room.room_line_ids.filtered(
#             lambda line: line.reservation_line_id.id == reservation_line.id
#         )
#         # update reservation (dates) in rooms
#         if checkout:
#             room_reservation_line.write({"check_out": checkout})
#             room_line_id.write({"check_out": checkout})

#     def update_folio_invoice(self, room_line, room, checkout, duration, is_change_rent):
#         """Update folio and invoice"""
#         if room_line.reservation_line_id:
#             # Update Rooms and folio reservation lines
#             room_line.write(
#                 {
#                     "checkout_date": checkout,
#                     "product_uom_qty": int(duration),
#                 }
#             )
#             self.update_room_reservation_line(
#                 room_line.reservation_line_id, room, checkout
#             )
#             # update invoice qty
#             if self.folio_id.hotel_invoice_id:
#                 room_line.invoice_lines.with_context(
#                     check_move_validity=False
#                 ).quantity = duration
#             if is_change_rent or room_line.reservation_line_id.peak_days:
#                 # update price unit in folio and invoice
#                 price_unit = self.get_price(
#                     room_line.reservation_line_id.other_price,
#                     self.rent,
#                     room,
#                     self.company_id,
#                     room_line.checkin_date,
#                     checkout,
#                     duration,
#                 )
#                 # update prices
#                 room_line.price_unit = price_unit
#                 if room_line.reservation_line_id.line_id.folio_id.hotel_invoice_id:
#                     room_line.invoice_lines.with_context(
#                         check_move_validity=False
#                     ).write({"price_unit": price_unit})

#     def get_discount_insurance(
#         self, folio_line, invoice_line, checkin, checkout, product, price_unit, name
#     ):
#         """Update insurance and discount in reservation"""
#         # update unit price if there is a line in folio
#         if folio_line:
#             folio_line[0].price_unit = price_unit
#         else:
#             # create new folio line if there is a no line in folio
#             if product:
#                 folio_line = self.env["hotel.folio.line"].create(
#                     {
#                         "checkin_date": checkin,
#                         "folio_id": self.folio_id.id,
#                         "checkout_date": checkout,
#                         "product_id": product.id,
#                         "name": name,
#                         "price_unit": price_unit,
#                         "product_uom_qty": 1,
#                         "is_reserved": True,
#                     }
#                 )

#         folio_line._onchange_product_id()
#         folio_line.price_unit = price_unit
#         if self.folio_id.hotel_invoice_id:
#             if invoice_line:
#                 # update unit price if there is a line in invoice
#                 invoice_line[0].with_context(
#                     check_move_validity=False
#                 ).price_unit = price_unit
#             else:
#                 # create new invoice line if there is a no line in invoice
#                 accounts = False
#                 fiscal_position = self.folio_id.hotel_invoice_id.fiscal_position_id
#                 if fiscal_position:
#                     accounts = product.product_tmpl_id.with_company(
#                         self.company_id
#                     ).get_product_accounts(fiscal_pos=fiscal_position)
#                 invoice = self.folio_id.hotel_invoice_id
#                 invoice_line = (
#                     self.env["account.move.line"]
#                     .with_context(check_move_validity=False)
#                     .create(
#                         {
#                             "product_id": product.id,
#                             "quantity": 1,
#                             "price_unit": price_unit,
#                             "move_id": self.folio_id.hotel_invoice_id.id,
#                             "account_id": accounts["income"].id
#                             if accounts
#                             else invoice.journal_id.default_account_id.id,
#                         }
#                     )
#                 )

#                 invoice_line.with_context(
#                     check_move_validity=False
#                 )._onchange_product_id()
#                 invoice_line.with_context(
#                     check_move_validity=False
#                 ).price_unit = price_unit
#                 self.folio_id.hotel_invoice_id.with_context(
#                     check_move_validity=False
#                 ).invoice_line_ids += invoice_line
#                 folio_line.invoice_lines = [
#                     (
#                         4,
#                         invoice_line.id,
#                     )
#                 ]

#     def update_discount_folio_invoice(self, reservation_line_id):
#         """Update discount"""
#         discount_product = self.env["product.product"].search(
#             [("discount", "=", True)], limit=1
#         )
#         folio_discount = self.folio_id.room_line_ids.filtered(
#             lambda discount_line: discount_line.product_id.discount
#         )
#         line_discount = self.folio_id.hotel_invoice_id.invoice_line_ids.filtered(
#             lambda discount_line: discount_line.product_id.discount
#         )
#         # calculate discount
#         self.get_discount_insurance(
#             folio_discount,
#             line_discount,
#             self.checkin,
#             reservation_line_id.date_extension
#             if reservation_line_id and reservation_line_id.date_extension
#             else self.checkout,
#             discount_product,
#             -(self.discount + self.discount_change_room)
#             if not self.is_hospitality
#             else -(self.discount + self.discount_change_room + self.taxes_amount),
#             _("Discount"),
#         )

#     def update_returnable_folio_invoice(self, reservation_line_id):
#         """Update returnable"""
#         returnable_product = self.env["product.product"].search(
#             [("returnable", "=", True)], limit=1
#         )
#         folio_returnable = self.folio_id.room_line_ids.filtered(
#             lambda returnable_line: returnable_line.product_id.returnable
#         )
#         line_returnable = self.folio_id.hotel_invoice_id.invoice_line_ids.filtered(
#             lambda returnable_line: returnable_line.product_id.returnable
#         )
#         self.get_discount_insurance(
#             folio_returnable,
#             line_returnable,
#             self.checkin,
#             reservation_line_id.date_extension
#             if reservation_line_id and reservation_line_id.date_extension
#             else self.checkout,
#             returnable_product,
#             self.returnable_amount,
#             _("Returnable"),
#         )

#     def update_discount_insurance_returnable_folio(
#         self, discount, returnable, reservation_line_id
#     ):
#         """Update Insurance, amount returnable and discount in folio and invoice."""
#         # Update discount
#         folio_discount = self.folio_id.room_line_ids.filtered(
#             lambda discount_line: discount_line.product_id.discount
#         )
#         if discount or folio_discount:
#             self.update_discount_folio_invoice(reservation_line_id)
#         # Update returnable
#         if returnable:
#             self.update_returnable_folio_invoice(reservation_line_id)

#     def create_folio_line(
#         self,
#         folio,
#         reservation_line_id,
#         room,
#         checkin,
#         checkout,
#         duration,
#         price_unit,
#         discount,
#         insurance,
#     ):
#         """Create lines in folio and invoice"""
#         # create new folio line if there is a change rooms
#         line = self.env["hotel.folio.line"].create(
#             {
#                 "reservation_line_id": reservation_line_id.id,
#                 "checkin_date": checkin,
#                 "folio_id": folio.id,
#                 "checkout_date": checkout,
#                 "product_id": room.product_id and room.product_id.id,
#                 "name": self["reservation_no"],
#                 "price_unit": price_unit,
#                 "product_uom_qty": duration,
#                 "is_reserved": True,
#             }
#         )
#         line._onchange_product_id()
#         line.price_unit = price_unit

#         # Create line invoice
#         if folio.hotel_invoice_id:
#             accounts = False
#             fiscal_position = folio.hotel_invoice_id.fiscal_position_id
#             if fiscal_position:
#                 accounts = room.product_id.product_tmpl_id.with_company(
#                     self.company_id
#                 ).get_product_accounts(fiscal_pos=fiscal_position)
#             # create new invoice line if there is a change rooms
#             line_invoice = (
#                 self.env["account.move.line"]
#                 .with_context(check_move_validity=False)
#                 .create(
#                     {
#                         "product_id": room.product_id.id,
#                         "quantity": duration,
#                         "price_unit": price_unit,
#                         "move_id": folio.hotel_invoice_id.id,
#                         "account_id": accounts["income"].id
#                         if accounts
#                         else folio.hotel_invoice_id.journal_id.default_account_id.id,
#                     }
#                 )
#             )
#             line_invoice.with_context(check_move_validity=False)._onchange_product_id()
#             line_invoice.with_context(check_move_validity=False).tax_ids = line.tax_id
#             line_invoice.with_context(check_move_validity=False).price_unit = price_unit
#             line.invoice_lines = [
#                 (
#                     4,
#                     line_invoice.id,
#                 )
#             ]

#             # update insurance and discount and returnable amount in folio and invoice
#         self.update_discount_insurance_returnable_folio(
#             discount, self.returnable_amount, reservation_line_id
#         )

#     def prepare_folio_lines(
#         self, reservation, folio_lines, checkin_date, checkout_date
#     ):
#         """Prepare folio lines."""
#         for line in reservation.reservation_line:
#             # Calculate price room based on rent type
#             # for room in line.reserve:
#             if line.line_id.rent == "daily":
#                 price_unit = line.room_id.list_price
#             elif line.line_id.rent == "monthly":
#                 price_unit = line.room_id.monthly_price
#             else:
#                 price_unit = line.room_id.hourly_price
#             # get peak price
#             peak_price = line.calculate_peak_room_price(
#                 reservation.rent,
#                 line.room_id,
#                 reservation.company_id.id,
#                 reservation.checkin,
#                 reservation.checkout,
#                 reservation.duration,
#             )
#             price_unit = peak_price if peak_price else price_unit
#             if line.is_minimum_price or line.is_other_price:
#                 price_unit = line.other_price
#             folio_lines.append(
#                 (
#                     0,
#                     0,
#                     {
#                         "reservation_line_id": line.id,
#                         "checkin_date": checkin_date,
#                         "checkout_date": checkout_date,
#                         "product_id": line.room_id.product_id
#                         and line.room_id.product_id.id,
#                         "name": reservation["reservation_no"],
#                         "price_unit": price_unit,
#                         "product_uom_qty": reservation.duration,
#                         "is_reserved": True,
#                     },
#                 )
#             )
#             line.room_id.write({"status": "occupied", "isroom": False})
#         # Calculate discount
#         if reservation.discount:
#             discount_product = self.env["product.product"].search(
#                 [("discount", "=", True)], limit=1
#             )
#             folio_lines.append(
#                 (
#                     0,
#                     0,
#                     {
#                         "checkin_date": checkin_date,
#                         "checkout_date": checkout_date,
#                         "product_id": discount_product and discount_product.id,
#                         "name": _("Discount"),
#                         "price_unit": -reservation.discount
#                         if not self.is_hospitality
#                         else -(
#                             reservation.discount
#                             + reservation.discount_change_room
#                             + reservation.taxes_amount
#                         ),
#                         "product_uom_qty": 1,
#                     },
#                 )
#             )
#         # Calculate returnable
#         if reservation.is_returnable and reservation.returnable_amount:
#             returnable_product = self.env["product.product"].search(
#                 [("returnable", "=", True)], limit=1
#             )
#             folio_lines.append(
#                 (
#                     0,
#                     0,
#                     {
#                         "checkin_date": checkin_date,
#                         "checkout_date": checkout_date,
#                         "product_id": returnable_product and returnable_product.id,
#                         "name": _("Recovery"),
#                         "price_unit": reservation.returnable_amount,
#                         "product_uom_qty": 1,
#                     },
#                 )
#             )
#         return folio_lines

#     def create_folio(self):
#         """
#         This method is for create new hotel folio.
#         -----------------------------------------
#         @param self: The object pointer
#         @return: new record set for hotel folio.
#         """
#         hotel_folio_obj = self.env["hotel.folio"]
#         for reservation in self:
#             folio_lines = []
#             checkin_date = reservation["checkin"]
#             checkout_date = reservation["checkout"]
#             warehouse = reservation.env["stock.warehouse"].search(
#                 [("company_id", "=", reservation.company_id.id)], limit=1
#             )
#             # prepare folio vals
#             folio_vals = {
#                 "date_order": reservation.date_order,
#                 "company_id": reservation.company_id.id,
#                 "warehouse_id": warehouse.id,
#                 "partner_id": reservation.partner_id.id,
#                 "partner_invoice_id": reservation.partner_invoice_id.id,
#                 "partner_shipping_id": reservation.partner_shipping_id.id,
#                 "checkin_date": reservation.checkin,
#                 "checkout_date": reservation.checkout,
#                 "duration": reservation.duration,
#                 "reservation_id": reservation.id,
#             }
#             folio_lines = reservation.prepare_folio_lines(
#                 reservation, folio_lines, checkin_date, checkout_date
#             )
#             folio_vals.update({"room_line_ids": folio_lines})
#             # create folio
#             folio = hotel_folio_obj.create(folio_vals)
#             for rm_line in folio.room_line_ids:
#                 price_unit = rm_line.price_unit
#                 rm_line._onchange_product_id()
#                 rm_line.price_unit = price_unit
#             self.write({"folio_id": [(6, 0, folio.ids)], "state": "done"})
#         return True

#     def send_shomoos(self):
#         """send to shomoos."""
#         self.write({"is_send_shomoos": not self.is_send_shomoos})

#     def send_tourism(self):
#         """send to tourism."""
#         self.write({"is_send_tourism": not self.is_send_tourism})

#     def get_duration(self, rent, date_from, date_to):
#         """Calculate duration."""
#         if rent == "daily":
#             if date_from.date() == date_to.date():
#                 duration = 1
#             else:
#                 duration = (date_to.date() - date_from.date()).days

#         elif rent == "monthly":
#             duration = (date_to.date() - date_from.date()).days / 30
#         else:
#             duration = (date_to - date_from).total_seconds() / 3600
#         return round(duration)

#     def open_folio_view(self):
#         folios = self.mapped("folio_id")
#         action = self.env.ref("hotel.open_hotel_folio1_form_tree_all").sudo().read()[0]
#         if len(folios) > 1:
#             action["domain"] = [("id", "in", folios.ids)]
#         elif len(folios) == 1:
#             action["views"] = [(self.env.ref("hotel.view_hotel_folio_form").id, "form")]
#             action["res_id"] = folios.id
#         else:
#             action = {"type": "ir.actions.act_window_close"}
#         return action

#     @api.onchange("checkin", "checkout", "rent")
#     def _onchange_checkin_checkout(self):
#         """Calculate duration"""
#         self.duration = 0
#         if self.checkin and self.checkout:
#             self.duration = self.get_duration(self.rent, self.checkin, self.checkout)
#             if not self._context.get("default_type_state") and not (
#                 self.checkin.date() == self.checkout.date() and self.rent == "daily"
#             ):
#                 self._onchange_duration()

#     def get_hour_setting(self):
#         """Get hour setting"""
#         hour, minute = 0, 0
#         hour_setting = self.env["hotel.reservation.setting"].search(
#             [("company_id", "=", self.company_id.id)], limit=1
#         )
#         if hour_setting and hour_setting.hours_day:
#             hour, minute = self.get_hour_minute_float(hour_setting.hours_day)
#         return hour_setting, hour, minute

#     @api.onchange("duration", "rent")
#     def _onchange_duration(self):
#         if self.duration:
#             hour_setting, hour, minute = self.get_hour_setting()
#             # calculate checkout and check in
#             checkout = self.checkout
#             self.checkout = 0
#             if self.rent == "daily":
#                 if (
#                     self.duration == 1
#                     and checkout
#                     and self.checkin.date() == checkout.date()
#                 ):
#                     checkin = self.checkin
#                 else:
#                     checkin = self.checkin + relativedelta(days=int(self.duration))
#             elif self.rent == "monthly":
#                 checkin = self.checkin + relativedelta(days=int(self.duration * 30))
#             else:
#                 checkin = self.checkin + relativedelta(hours=int(self.duration))
#             # change checkout date based on hour setting
#             if hour_setting and self.rent in ["daily", "monthly"]:
#                 tz_diff = (
#                     checkin.astimezone(pytz.timezone("Asia/Riyadh")).replace(
#                         tzinfo=None
#                     )
#                     - checkin
#                 )
#                 tz_diff = tz_diff.seconds / 3600
#                 checkin = checkin.replace(
#                     hour=hour - int(tz_diff), minute=minute, second=0
#                 )
#             self.checkout = checkin

#     def get_price(
#         self, other_price, rent, room_id, company, checkin, checkout, duration
#     ):
#         """Get room price"""
#         if rent == "daily":
#             price = room_id.list_price
#         elif rent == "monthly":
#             price = room_id.monthly_price
#         else:
#             price = room_id.hourly_price
#         # calculate peak price
#         peak_price = self.env["hotel.reservation.line"].calculate_peak_room_price(
#             rent,
#             room_id,
#             company.id,
#             checkin,
#             checkout,
#             duration,
#         )
#         price_room = peak_price if peak_price else price
#         return other_price if other_price else price_room

#     def get_duration_change_room(self, date_from, date_to, rent):
#         """Get duration for change rooms"""
#         if rent == "daily":
#             duration = (date_to.date() - date_from.date()).days
#             if date_to.date() == date_from.date():
#                 duration = +1
#         elif rent == "monthly":
#             duration = (date_to.date() - date_from.date()).days / 30
#         else:
#             duration = (date_to - date_from).total_seconds() / 3600
#         return round(duration)

#     def calculate_old_room_prices(self, reservation, line, rent):
#         """Calculate price and duration and taxesold rooms"""
#         all_price = 0
#         taxes_amount = 0
#         all_duration = 1
#         for history in reservation.env["reservation.room.change.history"].search(
#             [("reservation_line_id", "=", line.id), ("is_no_calculated", "=", False)]
#         ):
#             if rent == "hours" or (
#                 rent in ["daily", "monthly"]
#                 and history.change_date.date() != history.reservation_date.date()
#             ):
#                 duration = reservation.get_duration_change_room(
#                     history.reservation_date, history.change_date, rent
#                 )
#                 price = reservation.get_price(
#                     history.old_other_price,
#                     rent,
#                     history.old_room_id,
#                     reservation.company_id,
#                     history.reservation_date,
#                     history.change_date + relativedelta(days=int(-1)),
#                     duration,
#                 )
#                 all_duration += duration
#                 taxes = history.old_room_id.taxes_id.compute_all(
#                     price,
#                     history.old_room_id.currency_id,
#                     duration,
#                     product=history.old_room_id.product_id,
#                     partner=reservation.partner_shipping_id,
#                 )
#                 taxes_amount += sum(
#                     tax.get("amount", 0.0) for tax in taxes.get("taxes", [])
#                 )
#                 all_price += taxes["total_excluded"]
#         return all_price, int(all_duration) - 1, taxes_amount, taxes

#     @api.onchange("reservation_line")
#     def _onchange_reservation_line(self):
#         """Calculate insurance."""
#         insurance = 0
#         for room in self.reservation_line.mapped("room_id"):
#             insurance += room.insurance
#         self.insurance = (
#             self.insurance_change_room if self.insurance_change_room else insurance
#         )

#     @api.depends(
#         "reservation_line",
#         "reservation_line.total_room_rate",
#         "reservation_line.other_price",
#         "reservation_line.peak_price",
#         "reservation_line.peak_days",
#         "duration",
#         "discount_type",
#         "discount_percentage",
#         "returnable_percentage",
#         "discount",
#         "insurance",
#         "reservation_line.discount_change_room",
#         "insurance_change_room",
#         "reservation_line.date_extension",
#         "service_amount",
#         "rent",
#         "checkin",
#         "checkout",
#     )
#     def _compute_total_room_rate(self):
#         """Calculate Costs."""
#         for reservation in self:
#             taxes_amount = 0
#             taxes_info = {}
#             reservation.taxes_info = ""
#             reservation.room_rate = reservation.total_room_rate = 0
#             for line in reservation.reservation_line:
#                 duration = (
#                     reservation.duration
#                     if not line.date_extension
#                     else line.duration_extension
#                 )
#                 history = reservation.history_room_ids.filtered(
#                     lambda history: history.reservation_line_id.id == line.id
#                     and not history.is_no_calculated
#                 )
#                 room = line.room_id
#                 other_price = line.other_price
#                 checkin = reservation.checkin
#                 checkout = (
#                     line.date_extension if line.date_extension else reservation.checkout
#                 )
#                 if (
#                     line.date_termination
#                     and reservation.reservation_type == "collective"
#                     and reservation.is_returnable
#                 ):
#                     duration = line.duration_termination
#                     checkout = line.date_termination
#                 # Get duration and taxes and prices of old rooms
#                 # when change rooms that we didn't terminate it
#                 old_room_taxes = False
#                 if len(history):
#                     if line.date_termination:
#                         history = reservation.history_room_ids.filtered(
#                             lambda history: history.reservation_line_id.id == line.id
#                             and not history.is_no_calculated
#                             and history.change_date.date()
#                             <= line.date_termination.date()
#                         )
#                     if history:
#                         room = history[-1].room_id
#                         other_price = history[-1].other_price
#                         (
#                             all_price,
#                             all_duration,
#                             taxes_amount_change,
#                             old_room_taxes,
#                         ) = reservation.calculate_old_room_prices(
#                             reservation, line, reservation.rent
#                         )
#                         checkin = history[-1].change_date
#                         duration = reservation.get_duration_change_room(
#                             history[-1].change_date, checkout, reservation.rent
#                         )
#                         if reservation.rent == "daily":
#                             duration = duration
#                 price = reservation.get_price(
#                     other_price,
#                     reservation.rent,
#                     room,
#                     reservation.company_id,
#                     checkin,
#                     checkout,
#                     duration,
#                 )
#                 taxes = room.taxes_id.compute_all(
#                     price,
#                     room.currency_id,
#                     duration,
#                     product=room.product_id,
#                     partner=reservation.partner_shipping_id,
#                 )
#                 # calculte amount tax and tax info
#                 all_taxes = taxes.get("taxes", [])
#                 if old_room_taxes and old_room_taxes.get("taxes", []):
#                     all_taxes += list(old_room_taxes.get("taxes", []))
#                 for tax in all_taxes:
#                     if str(tax.get("name")) not in taxes_info:
#                         taxes_info[str(tax.get("name"))] = tax.get("amount")
#                     else:
#                         taxes_info[str(tax.get("name"))] = taxes_info.get(
#                             str(tax.get("name"))
#                         ) + tax.get("amount")
#                     taxes_amount += tax.get("amount", 0.0)

#                 if len(history):
#                     reservation.total_room_rate += taxes["total_excluded"] + all_price
#                     price = (
#                         (taxes["total_excluded"] + all_price)
#                         / (duration + all_duration)
#                         if (duration + all_duration)
#                         else 0
#                     )
#                     reservation.room_rate += price
#                     duration = (
#                         reservation.duration
#                         if not line.date_extension
#                         else line.duration_extension
#                     )
#                 else:
#                     reservation.total_room_rate += taxes["total_excluded"]
#                     reservation.room_rate += price
#             # tax info
#             for tax_info in taxes_info:
#                 reservation.taxes_info += "%s : %s \n" % (
#                     tax_info,
#                     "%.2f" % taxes_info.get(tax_info),
#                 )
#             reservation.total_room_rate += reservation.service_amount
#             reservation.discount = (
#                 reservation.discount
#                 if reservation.discount_type == "amount"
#                 else (reservation.discount_percentage * reservation.total_room_rate)
#                 / 100
#             )
#             # calculate discount when change rooms
#             reservation.discount_change_room = sum(
#                 reservation.reservation_line.mapped("discount_change_room")
#             )
#             reservation.total_cost = (
#                 reservation.total_room_rate
#                 - reservation.discount
#                 - reservation.discount_change_room
#             )

#             reservation.taxes_amount = taxes_amount + reservation.service_tax

#             reservation.taxed_total_rate = (
#                 (reservation.taxes_amount + reservation.total_cost)
#                 if not reservation.is_hospitality
#                 else 0
#             )
#             reservation.returnable_amount = (
#                 reservation.taxed_total_rate * reservation.returnable_percentage
#             ) / 100
#             reservation.final_cost = (
#                 (
#                     reservation.taxed_total_rate
#                     + reservation.insurance
#                     + reservation.returnable_amount
#                 )
#                 if not reservation.is_hospitality
#                 else 0
#             )

#     @api.model
#     def cron_change_room_reservation_daily(self):
#         """Cron for termination and change rooms"""
#         change_room_reservation = self.env["reservation.room.change.history"].search(
#             [("is_no_calculated", "=", False)]
#         )
#         # for change rooom ( change room and update room state)
#         for history in change_room_reservation.filtered(
#             lambda history: (
#                 history.reservation_line_id.line_id.rent != "hours"
#                 and history.change_date.date() == datetime.today().date()
#             )
#         ):
#             history.reservation_line_id.room_id.write(
#                 {"is_clean": False, "status": "available"}
#             )
#             history.reservation_line_id.room_id = history.room_id.id
#             history.reservation_line_id.other_price = history.other_price
#             if history.reservation_id.reservation_type == "individual":
#                 history.reservation_id.partner_id.last_room_id = (
#                     history.reservation_line_id.room_id.id
#                 )
#             else:
#                 partner = (
#                     history.reservation_line_id.partner_id
#                     if history.reservation_line_id.tenant == "person"
#                     else history.reservation_line_id.partner_company_id
#                 )
#                 partner.last_room_id = history.reservation_line_id.room_id.id
#             history.reservation_line_id.room_id.status = "occupied"

#     @api.model
#     def cron_change_room_reservation_hours(self):
#         """Cron for termination and change rooms"""
#         change_room_reservation = self.env["reservation.room.change.history"].search(
#             [("is_no_calculated", "=", False)]
#         )
#         for history in change_room_reservation.filtered(
#             lambda history: (
#                 history.reservation_line_id.line_id.rent == "hours"
#                 and history.change_date.date() == datetime.today().date()
#                 and history.change_date.hour == datetime.today().hour
#             )
#         ):
#             history.reservation_line_id.room_id.write(
#                 {"is_clean": False, "status": "available"}
#             )
#             history.reservation_line_id.room_id = history.room_id.id
#             history.reservation_line_id.room_id = history.other_price
#             history.reservation_line_id.room_id.status = "occupied"

#     @api.depends("payment_ids.amount", "payment_ids.support_type_id")
#     def _compute_payment_totals(self):
#         for reservation in self:
#             totals = {}
#             for line in reservation.payment_ids.filtered(
#                 lambda payment: payment.state == "posted"
#                 and payment.payment_type == "inbound"
#             ):
#                 if line.support_type_id.name not in totals:
#                     totals[line.support_type_id.name] = 0
#                 totals[line.support_type_id.name] += line.amount
#             formatted_totals = "\n".join(
#                 f"{key}: {value}" for key, value in totals.items()
#             )
#             reservation.payment_totals = formatted_totals

#     @api.depends(
#         "partner_id.invoice_ids.amount_residual",
#         "folio_id",
#         "partner_id",
#         "payment_ids",
#         "payment_ids.state",
#         "folio_id.hotel_invoice_id",
#         "folio_id.hotel_invoice_id.payment_state",
#         "folio_id.hotel_invoice_id.state",
#         "folio_id.hotel_invoice_id.reversal_move_id",
#         "folio_id.hotel_invoice_id.reversal_move_id.amount_residual",
#         "folio_id.hotel_invoice_id.line_ids",
#         "folio_id.hotel_invoice_id.line_ids.amount_residual",
#         "final_cost",
#     )
#     def _compute_payments(self):
#         """Calculate payments and balance and payments details ."""
#         for reservation in self:
#             reservation.balance = (
#                 reservation.payments_count
#             ) = reversed_entry_payment = 0
#             if reservation.folio_id.hotel_invoice_id:
#                 if reservation.folio_id.hotel_invoice_id.reversal_move_id:
#                     # flake8: noqa: B950
#                     for (
#                         reversal_move
#                     ) in reservation.folio_id.hotel_invoice_id.reversal_move_id:
#                         reversed_entry_payment += sum(
#                             payment_reversed["amount"]
#                             for payment_reversed in reversal_move._get_reconciled_info_JSON_values()
#                         )
#                 # flake8: noqa: B950
#                 reservation.payments_count = (
#                     sum(
#                         payment["amount"]
#                         for payment in reservation.folio_id.hotel_invoice_id._get_reconciled_info_JSON_values()
#                     )
#                     - reversed_entry_payment
#                 )
#             # calculate payment based on payments of reservation
#             payments_supplier_amount = sum(
#                 reservation.payment_ids.filtered(
#                     lambda payment_reservation: payment_reservation.payment_type
#                     == "outbound"
#                     and payment_reservation.state == "posted"
#                 ).mapped("amount")
#             )

#             payments = reservation.payment_ids.filtered(
#                 lambda payment_reservation: payment_reservation.payment_type
#                 == "inbound"
#                 and payment_reservation.state == "posted"
#             )
#             if payments:
#                 reservation.payments_count = sum(payments.mapped("amount"))
#             # calculate balance
#             reservation.balance = (
#                 reservation.payments_count
#                 - (reservation.final_cost - reservation.insurance)
#                 - payments_supplier_amount
#             )

#     @api.depends("date_check_in", "date_check_out", "rent")
#     def _compute_check_duration(self):
#         """Calculate Check Duration."""
#         for reservation in self:
#             reservation.duration_check = 0
#             if reservation.date_check_in and reservation.date_check_out:
#                 reservation.duration_check = reservation.get_duration(
#                     reservation.rent,
#                     reservation.date_check_in,
#                     reservation.date_check_out,
#                 )

#     def _compute_display_button_reservation(self):
#         """Display buttons reservation."""
#         for reservation in self:
#             reservation.display_button_terminate_reservation = (
#                 reservation.display_button_extend_reservation
#             ) = (
#                 reservation.display_button_check_in_reservation
#             ) = (
#                 reservation.display_button_check_out_reservation
#             ) = (
#                 reservation.display_button_cancel
#             ) = reservation.display_button_returned_reservation = False
#             today = (
#                 datetime.today()
#                 if reservation.rent == "hours"
#                 else datetime.today().date()
#             )
#             checkin = (
#                 reservation.checkin
#                 if reservation.rent == "hours"
#                 else reservation.checkin.date()
#             )
#             checkout = (
#                 reservation.checkout
#                 if reservation.rent == "hours"
#                 else reservation.checkout.date()
#             )
#             date_termination = False
#             if reservation.date_termination:
#                 date_termination = (
#                     reservation.date_termination
#                     if reservation.rent == "hours"
#                     else reservation.date_termination.date()
#                 )
#             # display button cancel
#             if reservation.state in ["draft", "confirm"]:
#                 reservation.display_button_cancel = True
#             if reservation.state == "done":
#                 # display button terminate
#                 if (
#                     reservation.reservation_type == "individual"
#                     and not reservation.date_check_out
#                     and not reservation.date_termination
#                     and reservation.date_check_in
#                     and (
#                         (
#                             reservation.checkin
#                             < datetime.today()
#                             < reservation.checkout
#                             and reservation.rent == "hours"
#                         )
#                         or (
#                             reservation.checkin < datetime.today()
#                             and datetime.today().date() < reservation.checkout.date()
#                             and reservation.rent != "hours"
#                         )
#                     )
#                 ) or (
#                     reservation.reservation_type == "collective"
#                     and reservation.reservation_line.filtered(
#                         lambda line: not line.date_termination
#                         and line.date_check_in
#                         and not line.date_check_out
#                         and (
#                             (
#                                 not line.date_extension
#                                 and reservation.checkin
#                                 < datetime.today()
#                                 < reservation.checkout
#                             )
#                             or (
#                                 line.date_extension
#                                 and reservation.checkin
#                                 < datetime.today()
#                                 < line.date_extension
#                             )
#                         )
#                     )
#                 ):
#                     reservation.display_button_terminate_reservation = True
#                 # display button extension
#                 if not reservation.is_returnable_reservation and (
#                     (
#                         reservation.reservation_type == "individual"
#                         and not reservation.date_check_out
#                         and not reservation.date_termination
#                         and (
#                             (date_termination and date_termination >= today)
#                             or checkout >= today
#                         )
#                     )
#                     or (
#                         reservation.reservation_line.filtered(
#                             lambda line: not line.date_check_out
#                             and not line.date_termination
#                             and (
#                                 (
#                                     (
#                                         reservation.rent != "hours"
#                                         and line.date_termination
#                                         and line.date_termination.date()
#                                         >= datetime.today().date()
#                                     )
#                                     or (
#                                         reservation.rent == "hours"
#                                         and line.date_termination
#                                         and line.date_termination >= datetime.today()
#                                     )
#                                 )
#                                 or (
#                                     (
#                                         reservation.rent != "hours"
#                                         and not line.date_extension
#                                         and line.line_id.checkout.date()
#                                         >= datetime.today().date()
#                                     )
#                                     or (
#                                         reservation.rent == "hours"
#                                         and not line.date_extension
#                                         and line.line_id.checkout >= datetime.today()
#                                     )
#                                 )
#                                 or (
#                                     (
#                                         reservation.rent != "hours"
#                                         and line.date_extension
#                                         and line.date_extension.date()
#                                         >= datetime.today().date()
#                                     )
#                                     or (
#                                         reservation.rent == "hours"
#                                         and line.date_extension
#                                         and line.date_extension.date()
#                                         >= datetime.today().date()
#                                     )
#                                 )
#                             )
#                         )
#                         and reservation.reservation_type == "collective"
#                     )
#                 ):
#                     reservation.display_button_extend_reservation = True
#                 # display button check in
#                 if (
#                     (
#                         not reservation.date_check_in
#                         and reservation.reservation_type == "individual"
#                     )
#                     or (
#                         reservation.reservation_line.filtered(
#                             lambda line: not line.date_check_in
#                         )
#                         and reservation.reservation_type == "collective"
#                     )
#                 ) and checkin <= today <= checkout:
#                     reservation.display_button_check_in_reservation = True
#                 # display button check out
#                 if (
#                     reservation.date_check_in
#                     and not reservation.date_check_out
#                     and reservation.reservation_type == "individual"
#                     and (
#                         (today >= checkout and not reservation.date_termination)
#                         or (
#                             reservation.rent != "hours"
#                             and reservation.date_termination
#                             and datetime.today().date()
#                             >= reservation.date_termination.date()
#                         )
#                         or (
#                             reservation.rent == "hours"
#                             and reservation.date_termination
#                             and datetime.today() >= reservation.date_termination
#                         )
#                     )
#                 ) or (
#                     reservation.reservation_line.filtered(
#                         lambda line: not line.date_check_out
#                         and line.date_check_in
#                         and (
#                             (
#                                 reservation.rent != "hours"
#                                 and (
#                                     (
#                                         line.date_termination
#                                         and datetime.today().date()
#                                         >= line.date_termination.date()
#                                     )
#                                     or (
#                                         not line.date_termination
#                                         and (
#                                             (
#                                                 reservation.checkout.date()
#                                                 <= datetime.today().date()
#                                                 and not line.date_extension
#                                             )
#                                             or (
#                                                 line.date_extension
#                                                 and line.date_extension.date()
#                                                 <= datetime.today().date()
#                                             )
#                                         )
#                                     )
#                                 )
#                             )
#                             or (
#                                 reservation.rent == "hours"
#                                 and (
#                                     (
#                                         line.date_termination
#                                         and datetime.today() >= line.date_termination
#                                     )
#                                     or (
#                                         not line.date_termination
#                                         and (
#                                             (
#                                                 reservation.checkout <= datetime.today()
#                                                 and not line.date_extension
#                                             )
#                                             or (
#                                                 line.date_extension
#                                                 and line.date_extension
#                                                 <= datetime.today()
#                                             )
#                                         )
#                                     )
#                                 )
#                             )
#                         )
#                     )
#                     and reservation.reservation_type == "collective"
#                 ):
#                     reservation.display_button_check_out_reservation = True

#                 # display button cancel
#                 if (
#                     not reservation.date_check_in
#                     and reservation.reservation_type == "individual"
#                 ) or (
#                     len(
#                         reservation.reservation_line.filtered(
#                             lambda line: not line.date_check_in
#                         )
#                     )
#                     == len(reservation.reservation_line)
#                     and reservation.reservation_type == "collective"
#                 ):
#                     reservation.display_button_cancel = True
#             # display button returned reservation
#             if (
#                 reservation.is_returnable
#                 and not reservation.is_returnable_reservation
#                 and (
#                     reservation.state == "cancel"
#                     or (
#                         reservation.state == "done"
#                         and reservation.reservation_line.filtered(
#                             lambda line: line.date_termination
#                         )
#                     )
#                 )
#             ):
#                 reservation.display_button_returned_reservation = True

#     @api.onchange("children_ids")
#     def _onchange_children_adults(self):
#         self.children = len(self.children_ids)

#     @api.onchange("reservation_type")
#     def _onchange_reservation_type(self):
#         if self.reservation_type:
#             self.adults = False
#             self.children = False
#             self.children_ids = False
#             self.adults_ids = False

#     @api.onchange("source_id")
#     def _onchange_source(self):
#         if self.source_id:
#             self.source_number = ""

#     @api.constrains("discount_type")
#     def _check_discount_type(self):
#         """Check reservation percentage and amount."""
#         for reservation in self:
#             if (
#                 reservation.discount_type == "percentage"
#                 and not reservation.discount_percentage
#             ):
#                 raise ValidationError(_("You should add discount percentage"))
#             if reservation.discount_type == "amount" and not reservation.discount:
#                 raise ValidationError(_("You should add discount amount"))

#     def get_hijri_date(self, georging_date, separator):
#         """Convert georging date to hijri date.

#         :return hijri date as a string value
#         """
#         if georging_date:
#             georging_date = georging_date.date()
#             georging_date = fields.Date.from_string(georging_date)
#             hijri_date = HijriDate(
#                 georging_date.year, georging_date.month, georging_date.day, gr=True
#             )
#             return (
#                 str(int(hijri_date.year)).zfill(2)
#                 + separator
#                 + str(int(hijri_date.month)).zfill(2)
#                 + separator
#                 + str(int(hijri_date.day))
#             )
#         return None

#     def button_returned_reservation(self):
#         self.is_returnable_reservation = True

#     def action_terminate_extend_reservation(self):
#         """Terminate and extend Reservation."""
#         wizard = self.env["hotel.reservation.finish.wizard"].create(
#             {"reservation_id": self.id, "origin_rent": self.rent}
#         )
#         if self._context.get("default_type_state") == "finish":
#             wizard.type = "finish"
#             name = _("Termination Reservation")
#         else:

#             wizard.type = "extension"
#             name = _("Extend Reservation")
#         return {
#             "name": name,
#             "res_model": "hotel.reservation.finish.wizard",
#             "view_mode": "form",
#             "res_id": wizard.id,
#             "type": "ir.actions.act_window",
#             "target": "new",
#             "context": {"default_type_reservation": self.reservation_type},
#         }

#     def create_post_invoice(self):
#         """Create and post invoice"""
#         if self.folio_id.state != "sale":
#             self.folio_id.action_confirm()
#         if not self.folio_id.hotel_invoice_id:
#             self.folio_id.create_invoices()
#         invoice = self.folio_id.hotel_invoice_id
#         invoice.action_post()

#     def update_folio_invoice_qty(self, room_line):
#         # update folio and invoice line based on setting hours
#         if room_line.product_uom_qty:
#             room = self.env["hotel.room"].search(
#                 [("product_id", "=", room_line.product_id.id)], limit=1
#             )
#             self.update_folio_invoice(
#                 room_line,
#                 room,
#                 room_line.checkout_date,
#                 room_line.product_uom_qty + 1,
#                 False,
#             )

#     def action_payment_create(self, payment_type, partner_type, account):
#         """Create payment"""
#         journal = self.env["account.journal"].search([("type", "=", "bank")], limit=1)
#         payment_method_id = (
#             self.env["account.payment.method"]
#             .search([("payment_type", "=", payment_type)], limit=1)
#             .id
#         )
#         other_payments = self.payment_ids.filtered(
#             lambda payment_reservation: payment_reservation.payment_type == payment_type
#             and payment_reservation.partner_type == partner_type
#             and payment_reservation.state not in ["posted", "cancel"]
#         )
#         vals = {
#             "payment_type": payment_type,
#             "partner_type": partner_type,
#             "partner_id": self.partner_id.id,
#             "destination_account_id": account.id,
#             "payment_method_id": payment_method_id,
#             "amount": abs(self.balance) - sum(other_payments.mapped("amount")),
#             "ref": _("Reservation {}").format(self.reservation_no),
#             "company_id": self.company_id.id,
#             "date": fields.Datetime.now().date(),
#             "journal_id": journal.id,
#             "reservation_id": self.id,
#             "state": "draft",
#         }
#         payment = self.env["account.payment"].sudo().create(vals)
#         return payment

#     def action_check_in_check_out(self):
#         """Check in/out Reservation."""
#         if self.reservation_type == "individual":
#             # fill check in and check out
#             if self._context.get("default_check_type") == "in":
#                 self.date_check_in = datetime.today()
#                 self.partner_id.sudo().last_room_id = self.reservation_line[
#                     -1
#                 ].room_id.id
#                 # create and post invoice
#                 if not self.folio_id.hotel_invoice_id:
#                     self.create_post_invoice()
#             if self._context.get("default_check_type") == "out":
#                 checkout = (
#                     self.checkout
#                     if not self.date_termination
#                     else self.date_termination
#                 )
#                 self.date_check_out = datetime.today()
#                 self.create_housekeeping(self.reservation_line.mapped("room_id"))
#                 # send rating mail to customer
#                 self.rated_partner_id = self.partner_id
#                 self.send_rating_mail_customer(self.partner_id)
#                 self.reservation_line.mapped("room_id").write(
#                     {"is_clean": False, "status": "available"}
#                 )
#                 self.partner_id.sudo().last_room_id = False
#                 if self.date_check_out and self.date_termination and not self.balance:
#                     self.state = "finish"
#                 # create and post invoice
#                 if not self.hotel_invoice_id:
#                     self.create_post_invoice()
#                 # add day if time checkout excceed hours in setting
#                 hour_setting = self.env["hotel.reservation.setting"].search(
#                     [("company_id", "=", self.company_id.id)], limit=1
#                 )
#                 if hour_setting and hour_setting.hours_day:
#                     hour, minute = self.get_hour_minute_float(hour_setting.hours_day)
#                     if self.rent == "daily" and (
#                         self.date_check_out.date() > checkout.date()
#                         or (
#                             self.date_check_out.date() == checkout.date()
#                             and self._format_date(str(self.date_check_out)).time()
#                             > time(hour, minute, 0)
#                         )
#                     ):
#                         payments = self.payment_ids.filtered(
#                             lambda payment_reservation: payment_reservation.payment_type
#                             == "inbound"
#                             and payment_reservation.state == "posted"
#                         )
#                         self.duration += 1
#                         self._compute_total_room_rate()
#                         if self.folio_id.state != "draft":
#                             self.set_folio_draft()
#                             for room_line in self.folio_id.room_line_ids:
#                                 self.update_folio_invoice_qty(room_line)
#                     # post and confirm sale and invoice
#                     if self.folio_id.state == "draft":
#                         self.post_folio_invoice("sale", "posted", payments)
#                 # create payment outbound or inbound if the is a balance
#                 if self.balance:
#                     if self.balance > 0:
#                         payment = self.action_payment_create(
#                             "outbound",
#                             "customer",
#                             self.partner_id.with_company(
#                                 self.company_id
#                             ).property_account_payable_id,
#                         )
#                     else:
#                         payment = self.action_payment_create(
#                             "inbound",
#                             "customer",
#                             self.partner_id.with_company(
#                                 self.company_id
#                             ).property_account_receivable_id,
#                         )
#                     self.payment_ids += payment

#         else:
#             # open wizard to choose rooms
#             check_type = (
#                 "in" if self._context.get("default_check_type") == "in" else "out"
#             )
#             wizard = self.env["hotel.reservation.check.wizard"].create(
#                 {"reservation_id": self.id, "check_type": check_type}
#             )
#             context = self._context.copy()
#             if self._context.get("default_check_type") == "out":
#                 lines = self.reservation_line.filtered(
#                     lambda line: not line.date_check_out
#                     and line.date_check_in
#                     and (
#                         (
#                             line.date_termination
#                             and line.date_termination.date() <= datetime.today().date()
#                         )
#                         or (
#                             not line.date_termination
#                             and (
#                                 self.checkout.date() <= datetime.today().date()
#                                 and not line.date_extension
#                             )
#                             or (
#                                 line.date_extension
#                                 and line.date_extension.date()
#                                 <= datetime.today().date()
#                             )
#                         )
#                     )
#                 )
#                 context.update({"default_reservation_line_ids": lines.ids})
#             return {
#                 "name": _("Check In/Out Reservation"),
#                 "res_model": "hotel.reservation.check.wizard",
#                 "view_mode": "form",
#                 "res_id": wizard.id,
#                 "type": "ir.actions.act_window",
#                 "target": "new",
#                 "context": context,
#             }

#     def send_rating_mail_customer(self, partner):
#         """Send rating mail to customers"""
#         template = self.env.ref(
#             "hotel_reservation.rating_hotel_reservation_email_template",
#             raise_if_not_found=False,
#         )
#         if template:
#             mail_info = {
#                 "partner_id": partner.id,
#                 "partner_name": partner.name,
#                 "lang": partner.lang,
#                 "reservation_no": self.reservation_no,
#             }
#             template.sudo().email_to = partner.email
#             template.sudo().with_context(mail_info=mail_info).send_mail(
#                 self.id, force_send=True
#             )

#     def rating_get_partner_id(self):
#         """Get partner who are going to receive mail"""
#         res = super(HotelReservation, self).rating_get_partner_id()
#         if self.rated_partner_id:
#             return self.rated_partner_id
#         return res

#     def button_reservation_rating(self):
#         """OPen view Rating."""
#         reservation_rating = self.env["hotel.reservation.rating"].search(
#             [("company_id", "=", self.env.company.id)], limit=1
#         )
#         # Create rating view if the is no rating view
#         if not reservation_rating:
#             reservation_rating = (
#                 self.env["hotel.reservation.rating"]
#                 .sudo()
#                 .create(
#                     {
#                         "name": _("Rating %s") % self.env.company.name,
#                         "company_id": self.env.company.id,
#                     }
#                 )
#             )
#         value = {
#             "name": reservation_rating.name,
#             "view_type": "form",
#             "view_mode": "form",
#             "res_model": "hotel.reservation.rating",
#             "view_id": False,
#             "type": "ir.actions.act_window",
#             "res_id": reservation_rating.id,
#         }
#         return value


# class HotelReservationLine(models.Model):
#     _name = "hotel.reservation.line"
#     _description = "Reservation Line"
#     _rec_name = "room_id"

#     name = fields.Char("Name")
#     line_id = fields.Many2one("hotel.reservation")
#     room_id = fields.Many2one("hotel.room", string="Room")
#     rooms_available_ids = fields.Many2many(
#         "hotel.room",
#         "hotel_reservation_room_rel",
#         compute="_compute_rooms_available",
#         store=1,
#     )
#     categ_id = fields.Many2one("hotel.room.type", "Room Type")
#     total_room_rate = fields.Float(
#         string="Total Room Rate", compute="_compute_total_room_rate", store=1
#     )
#     reservation_type = fields.Selection(related="line_id.reservation_type", store=1)
#     tenant = fields.Selection(
#         string="Tenant",
#         selection=[("person", "Person"), ("company", "Company")],
#         default="person",
#     )
#     partner_id = fields.Many2one(
#         "res.partner",
#         "Person Name",
#     )
#     partner_company_id = fields.Many2one(
#         "res.partner",
#         "Company Name",
#     )
#     adults = fields.Integer(
#         "Number Adults",
#     )
#     children = fields.Integer(
#         "Number Children",
#     )
#     children_ids = fields.Many2many(
#         "res.partner",
#         "reservation_line_related_children_rel",
#         domain="[('is_guest', '=', True)]",
#         string="Children",
#     )
#     adults_ids = fields.Many2many(
#         "res.partner",
#         "reservation_line_related_adults_rel",
#         domain="[('is_guest', '=', True)]",
#         string="Adults",
#     )
#     date_check_in = fields.Datetime(string="Check in", readonly=1)
#     date_check_out = fields.Datetime("Check Out", readonly=1)
#     duration_check = fields.Integer(
#         string="Check Duration", compute="_compute_check_duration", store=1
#     )
#     peak_days = fields.Integer(string="Peak days", compute="_compute_peak_days")

#     peak_price = fields.Float(string="Peak price", compute="_compute_peak_days")
#     date_extension = fields.Datetime(string="Extension Date", readonly=1)
#     duration_extension = fields.Integer(
#         string="Extension Duration",
#         compute="_compute_duration_extension_termination",
#         store=1,
#     )
#     change_date = fields.Datetime(string="Change Date")
#     display_button_change_room = fields.Boolean(
#         string="Display button change room",
#         compute="_compute_display_button_change_room",
#     )
#     date_termination = fields.Datetime(string="Termination Date", readonly=1)
#     duration_termination = fields.Integer(
#         string="Termination Duration",
#         compute="_compute_duration_extension_termination",
#         store=1,
#     )
#     discount_change_room = fields.Float(string="Discount Change Room")
#     display_button_service_housekeeping = fields.Boolean(
#         string="Display button service housekeeping",
#         compute="_compute_display_service_housekeeping",
#     )
#     is_minimum_price = fields.Boolean(string="Minimum Prices")
#     is_other_price = fields.Boolean(string="Other Price")
#     other_price = fields.Float(string="Price")

#     @api.onchange("is_minimum_price")
#     def _onchange_is_minimum_price(self):
#         if not self.is_minimum_price:
#             self.other_price = 0
#         else:
#             self.is_other_price = False

#     @api.onchange("is_other_price")
#     def _onchange_is_other_price(self):
#         if not self.is_other_price:
#             self.other_price = 0
#         else:
#             self.is_minimum_price = False

#     def get_minimum_price_by_rent(self, rent, room):
#         if rent == "daily":
#             minimum_price = room.minimum_daily_price
#         elif rent == "monthly":
#             minimum_price = room.minimum_monthly_price
#         else:
#             minimum_price = room.minimum_hourly_price
#         return minimum_price

#     @api.constrains("is_other_price")
#     def _check_other_price(self):
#         for reservation_line in self:
#             if reservation_line.is_other_price:
#                 if not reservation_line.other_price:
#                     raise ValidationError(_("The Price must be more than 0"))
#                 if reservation_line.line_id.rent == "daily":
#                     price = reservation_line.room_id.list_price
#                 elif reservation_line.line_id.rent == "monthly":
#                     price = reservation_line.room_id.monthly_price
#                 else:
#                     price = reservation_line.room_id.hourly_price
#                 if price >= reservation_line.other_price:
#                     raise ValidationError(
#                         _("Other price must be greater than Room Price %s") % str(price)
#                     )

#     @api.constrains("is_minimum_price")
#     def _check_minimum_price(self):
#         for reservation_line in self:
#             if reservation_line.is_minimum_price:
#                 if not reservation_line.other_price:
#                     raise ValidationError(_("Minimum Price must be more than 0"))
#                 room_minimum_price = reservation_line.get_minimum_price_by_rent(
#                     reservation_line.line_id.rent, reservation_line.room_id
#                 )
#                 if room_minimum_price > reservation_line.other_price:
#                     raise ValidationError(
#                         _(
#                             "Minimum Price must be equal or greater than Room Minimum Price %s"
#                         )
#                         % room_minimum_price
#                     )

#     @api.onchange("tenant")
#     def _onchange_tenant(self):
#         if self.tenant == "person":
#             self.partner_company_id = False
#         if self.tenant == "company":
#             self.partner_id = False

#     @api.constrains("adults", "children")
#     def _check_guests(self):
#         """Check guests"""
#         for reservation_line in self:

#             if not reservation_line.room_id:
#                 raise ValidationError(_("Please Select Rooms For Reservation."))
#             # TODO check room capacity
#             # if (reservation_line.adults + reservation_line.children) > sum(
#             #     reservation_line.mapped("room_id.capacity")
#             # ):
#             #     raise ValidationError(
#             #         _(
#             #             "Room Capacity Exceeded \n"
#             #             " Please Select Rooms According to"
#             #             " Members Accomodation."
#             #         )
#             #     )

#     @api.onchange("children_ids", "adults_ids")
#     def _onchange_children_adults(self):
#         """Calculate children and aduls"""
#         self.children = len(self.children_ids)
#         self.adults = len(self.adults_ids)

#     @api.onchange("categ_id")
#     def on_change_categ(self):
#         """
#         When you change categ_id it check checkin and checkout are
#         filled or not if not then raise warning
#         -----------------------------------------------------------
#         @param self: object pointer
#         """
#         if not self.line_id.checkin:
#             raise ValidationError(
#                 _(
#                     """Before choosing a room,\n You have to """
#                     """select a Check in date or a Check out """
#                     """ date in the reservation form."""
#                 )
#             )
#         hotel_room_ids = self.env["hotel.room"].search(
#             [("room_categ_id", "=", self.categ_id.id), ("is_withheld", "=", False)]
#         )
#         room_ids = []
#         for room in hotel_room_ids:
#             assigned = False
#             for line in room.room_reservation_line_ids.filtered(
#                 lambda l: l.status != "cancel"
#             ):
#                 if self.line_id.checkin and line.check_in and self.line_id.checkout:
#                     if (
#                         self.line_id.checkin <= line.check_in <= self.line_id.checkout
#                     ) or (
#                         self.line_id.checkin <= line.check_out <= self.line_id.checkout
#                     ):
#                         assigned = True
#                     elif (line.check_in <= self.line_id.checkin <= line.check_out) or (
#                         line.check_in <= self.line_id.checkout <= line.check_out
#                     ):
#                         assigned = True
#             for rm_line in room.room_line_ids.filtered(lambda l: l.status != "cancel"):
#                 if self.line_id.checkin and rm_line.check_in and self.line_id.checkout:
#                     if (
#                         self.line_id.checkin
#                         <= rm_line.check_in
#                         <= self.line_id.checkout
#                     ) or (
#                         self.line_id.checkin
#                         <= rm_line.check_out
#                         <= self.line_id.checkout
#                     ):
#                         assigned = True
#                     elif (
#                         rm_line.check_in <= self.line_id.checkin <= rm_line.check_out
#                     ) or (
#                         rm_line.check_in <= self.line_id.checkout <= rm_line.check_out
#                     ):
#                         assigned = True
#             if not assigned:
#                 room_ids.append(room.id)
#         domain = {"room_id": [("id", "in", room_ids)]}
#         return {"domain": domain}

#     def unlink(self):
#         """
#         Overrides orm unlink method.
#         @param self: The object pointer
#         @return: True/False.
#         """
#         hotel_room_reserv_line_obj = self.env["hotel.room.reservation.line"]
#         for reservation_line in self:
#             room_reservation_line = hotel_room_reserv_line_obj.search(
#                 [
#                     ("room_id", "=", reservation_line.room_id.id),
#                     ("reservation_id", "=", reservation_line.line_id.id),
#                 ]
#             )
#             if room_reservation_line:
#                 reservation_line.room_id.write({"isroom": True, "status": "available"})
#                 room_reservation_line.unlink()
#         return super(HotelReservationLine, self).unlink()

#     def _compute_display_service_housekeeping(self):
#         """display button Service housekeeping"""
#         for reservation_line in self:
#             reservation_line.display_button_service_housekeeping = False
#             if (
#                 not reservation_line.room_id.is_clean
#                 and reservation_line.line_id.state == "done"
#             ):
#                 reservation_line.display_button_service_housekeeping = True

#     def _compute_display_button_change_room(self):
#         """display button chaneg rooms"""
#         for reservation_line in self:
#             reservation_line.display_button_change_room = False
#             if reservation_line.line_id.checkout:
#                 today = (
#                     datetime.today()
#                     if reservation_line.line_id.rent == "hours"
#                     else datetime.today().date()
#                 )
#                 checkout = (
#                     reservation_line.line_id.checkout
#                     if reservation_line.line_id.rent == "hours"
#                     else reservation_line.line_id.checkout.date()
#                 )
#                 date_termination = False
#                 date_extension = False
#                 if reservation_line.date_termination:
#                     date_termination = (
#                         reservation_line.date_termination
#                         if reservation_line.line_id.rent == "hours"
#                         else reservation_line.date_termination.date()
#                     )
#                 if reservation_line.date_extension:
#                     date_extension = (
#                         reservation_line.date_extension
#                         if reservation_line.line_id.rent == "hours"
#                         else reservation_line.date_extension.date()
#                     )
#                 if (
#                     reservation_line.line_id.state == "done"
#                     and not reservation_line.line_id.date_check_out
#                     and not reservation_line.date_check_out
#                     and (
#                         (date_termination and date_termination >= today)
#                         or (not reservation_line.date_extension and checkout >= today)
#                         or (reservation_line.date_extension and date_extension >= today)
#                     )
#                 ):
#                     reservation_line.display_button_change_room = True

#     @api.depends(
#         "room_id",
#         "room_id.list_price",
#         "room_id.monthly_price",
#         "room_id.hourly_price",
#         "line_id",
#         "line_id.rent",
#     )
#     def _compute_total_room_rate(self):
#         """Calculate room rate."""
#         for reservation_line in self:
#             if reservation_line.line_id.rent == "daily":
#                 reservation_line.total_room_rate = reservation_line.room_id.list_price
#             elif reservation_line.line_id.rent == "monthly":
#                 reservation_line.total_room_rate = (
#                     reservation_line.room_id.monthly_price
#                 )
#             else:
#                 reservation_line.total_room_rate = reservation_line.room_id.hourly_price

#     @api.depends(
#         "line_id.checkout",
#         "line_id",
#         "line_id.company_id",
#         "line_id.checkin",
#         "line_id.is_vip",
#         "line_id.adults",
#         "line_id.children",
#         "children",
#         "adults",
#     )
#     def _compute_rooms_available(self):
#         """Calculate avaibility rooms."""
#         for reservation_line in self:
#             reservation_line.rooms_available_ids = []
#             domain_suite = [
#                 ("room_categ_id.is_vip", "=", False),
#                 ("company_id", "=", reservation_line.line_id.company_id.id),
#             ]
#             if reservation_line.line_id.is_vip:
#                 domain_suite = [
#                     ("room_categ_id.is_vip", "=", True),
#                     ("company_id", "=", reservation_line.line_id.company_id.id),
#                 ]
#             if reservation_line.line_id.checkout and reservation_line.line_id.checkin:
#                 # get rooms by dates and capacity
#                 # TODO check room capacity
#                 available_rooms = (
#                     reservation_line.env["hotel.room"]
#                     .search(
#                         [
#                             ("is_withheld", "=", False),
#                             (
#                                 "id",
#                                 "not in",
#                                 reservation_line.line_id.reservation_line.mapped(
#                                     "room_id"
#                                 ).ids,
#                             ),
#                         ]
#                         + domain_suite
#                     )
#                     .filtered(
#                         lambda room: not room.get_status_room_dates(
#                             reservation_line.line_id,
#                             reservation_line.line_id.checkin,
#                             reservation_line.line_id.checkout,
#                         )
#                         and (
#                             (
#                                 reservation_line.line_id.reservation_type
#                                 == "individual"
#                                 # and room.capacity
#                                 # >= (
#                                 #     reservation_line.line_id.adults
#                                 #     + reservation_line.line_id.children
#                                 # )
#                             )
#                             or (
#                                 reservation_line.line_id.reservation_type
#                                 == "collective"
#                                 # and room.capacity
#                                 # >= (reservation_line.adults + reservation_line.children)
#                             )
#                         )
#                     )
#                 )
#                 if available_rooms:
#                     reservation_line.rooms_available_ids = available_rooms.ids

#     @api.depends("date_check_in", "date_check_out", "line_id.rent")
#     def _compute_check_duration(self):
#         """Calculate check duration."""
#         for reservation_line in self:
#             reservation_line.duration_check = 0
#             if reservation_line.date_check_in and reservation_line.date_check_out:
#                 reservation_line.duration_check = reservation_line.line_id.get_duration(
#                     reservation_line.line_id.rent,
#                     reservation_line.date_check_in,
#                     reservation_line.date_check_out,
#                 )

#     @api.depends(
#         "date_extension", "date_termination", "line_id.rent", "line_id.checkin"
#     )
#     def _compute_duration_extension_termination(self):
#         """Calculate extension and termination duration duration."""
#         for reservation_line in self:
#             reservation_line.duration_extension = (
#                 reservation_line.duration_termination
#             ) = 0
#             # Calculate extension duration
#             if reservation_line.line_id.checkin:
#                 if reservation_line.date_extension:
#                     reservation_line.duration_extension = (
#                         reservation_line.line_id.get_duration(
#                             reservation_line.line_id.rent,
#                             reservation_line.line_id.checkin,
#                             reservation_line.date_extension,
#                         )
#                     )
#                 # Calculate termination duration
#                 if reservation_line.date_termination:
#                     reservation_line.duration_termination = (
#                         reservation_line.line_id.get_duration(
#                             reservation_line.line_id.rent,
#                             reservation_line.line_id.checkin,
#                             reservation_line.date_termination,
#                         )
#                     )

#     def get_price_settings(self, categ, company, check_in, check_out):
#         """Get setting based on type room ans dates"""
#         if check_out and check_in and company and categ:
#             return self.env["price.setting"].search(
#                 [
#                     ("room_type_id", "=", categ),
#                     ("company_id", "=", company),
#                     "&",
#                     "|",
#                     "&",
#                     ("date_to", "<=", check_in.date()),
#                     ("date_from", ">=", check_out.date()),
#                     ("date_to", ">=", check_in.date()),
#                     ("date_from", "<=", check_out.date()),
#                 ]
#             )
#         return self.env["price.setting"]

#     def calculate_peak_room_days(self, rent, checkin, checkout, date_from, date_to):
#         """Calculate peak room days"""
#         peak_days = 0
#         if checkin.date() >= date_from:
#             if checkout.date() >= date_to:
#                 peak_days += relativedelta(date_to, checkin.date()).days + 1
#             elif checkout.date() <= date_to:
#                 peak_days += relativedelta(checkout.date(), checkin.date()).days + 1
#         else:
#             if checkout.date() >= date_to:
#                 peak_days += relativedelta(date_to, date_from).days + 1
#             elif checkout.date() <= date_to:
#                 peak_days += relativedelta(checkout.date(), date_from).days + 1
#         if rent == "daily" and checkin.date() != checkout.date():
#             peak_days -= 1
#         return peak_days

#     def calculate_peak_room_price(
#         self, rent, room, company, check_in, check_out, duration
#     ):
#         """Calculate peak room price"""
#         peak_by_room_days = 0
#         peak_room_price = 0
#         if rent == "daily":
#             price_unit = room.list_price
#         elif rent == "monthly":
#             price_unit_month = room.monthly_price
#             price_unit = price_unit_month / 30
#             if check_out and check_in:
#                 duration = (check_out - check_in).days
#         else:
#             price_unit = room.hourly_price
#             duration = (check_out - check_in).days + 1
#         for setting in self.get_price_settings(
#             room.room_categ_id.id, company, check_in, check_out
#         ):
#             peak_room_days = 0
#             peak_room_days += self.calculate_peak_room_days(
#                 rent, check_in, check_out, setting.date_from, setting.date_to
#             )
#             peak_by_room_days += self.calculate_peak_room_days(
#                 rent, check_in, check_out, setting.date_from, setting.date_to
#             )
#             amount = (
#                 (setting.amount * price_unit) / 100
#                 if setting.addition_type == "percentage"
#                 else setting.amount
#             )
#             peak_room_price += (amount + price_unit) * peak_room_days
#         peak_all_room_price = (
#             float(
#                 (peak_room_price + (price_unit * (duration - peak_by_room_days)))
#                 / duration
#             )
#             if duration
#             else 0
#         )
#         if rent == "monthly":
#             peak_all_room_price = peak_all_room_price * 30
#         return peak_all_room_price

#     def _compute_peak_days(self):
#         """Calculate peak days and price"""
#         for reservation_line in self:
#             peak_all_room_days = 0
#             peak_all_room_price = 0
#             checkout = (
#                 reservation_line.line_id.checkout
#                 if not reservation_line.date_extension
#                 else reservation_line.date_extension
#             )
#             duration = (
#                 reservation_line.line_id.duration
#                 if not reservation_line.date_extension
#                 else reservation_line.duration_extension
#             )
#             if reservation_line.date_termination:
#                 checkout = reservation_line.date_termination
#                 duration = reservation_line.duration_termination
#             if reservation_line.line_id.checkin and reservation_line.line_id.checkout:
#                 for setting in reservation_line.get_price_settings(
#                     reservation_line.room_id.room_categ_id.id,
#                     reservation_line.line_id.company_id.id,
#                     reservation_line.line_id.checkin,
#                     checkout,
#                 ):
#                     # Calculate peak days
#                     peak_all_room_days += self.calculate_peak_room_days(
#                         reservation_line.line_id.rent,
#                         reservation_line.line_id.checkin,
#                         checkout,
#                         setting.date_from,
#                         setting.date_to,
#                     )
#                 # Calculate peak price
#                 peak_all_room_price += self.calculate_peak_room_price(
#                     reservation_line.line_id.rent,
#                     reservation_line.room_id,
#                     reservation_line.line_id.company_id.id,
#                     reservation_line.line_id.checkin,
#                     checkout,
#                     duration,
#                 )
#             reservation_line.peak_days = peak_all_room_days
#             reservation_line.peak_price = (
#                 peak_all_room_price if peak_all_room_days else 0
#             )

#     def action_change_room(self):
#         """Change Room  Reservation."""
#         wizard = self.env["reservation.room.change.wizard"].create(
#             {
#                 "reservation_id": self.line_id.id,
#                 "reservation_line_id": self.id,
#                 "old_room_id": self.room_id.id,
#                 "origin_rent": self.line_id.rent,
#             }
#         )
#         return {
#             "name": _("Change Room"),
#             "res_model": "reservation.room.change.wizard",
#             "view_mode": "form",
#             "res_id": wizard.id,
#             "type": "ir.actions.act_window",
#             "target": "new",
#         }

#     def create_service_housekeeping(self):
#         """Create Cleanliness Service."""
#         # if there is housekeeping return it else create a new housekeeping
#         # search Cleanliness Service Housekeeping
#         housekeeping = (
#             self.env["hotel.housekeeping"]
#             .sudo()
#             .search(
#                 [
#                     ("type", "=", "cleanliness"),
#                     ("clean_type", "=", "checkin"),
#                     ("room_id", "=", self.room_id.id),
#                     ("reservation_id", "=", self.line_id.id),
#                 ],
#                 limit=1,
#             )
#         )
#         if not housekeeping:
#             # Prepare  Cleanliness Service Housekeeping vals
#             vals = {
#                 "reservation_id": self.line_id.id,
#                 "type": "cleanliness",
#                 "clean_type": "checkin",
#                 "room_id": self.room_id.id,
#                 "company_id": self.line_id.company_id.id,
#                 "inspect_date_time": fields.Datetime.now(),
#                 "categ_id": self.room_id.room_categ_id.id,
#             }
#             # Search Cleanliness Activity
#             activity = (
#                 self.env["hotel.activity"]
#                 .sudo()
#                 .search([("categ_id.type", "=", "cleanliness")], limit=1)
#             )
#             # Search Clean User
#             clean_user = (
#                 self.env["res.users"]
#                 .sudo()
#                 .search(
#                     [
#                         (
#                             "groups_id",
#                             "=",
#                             self.env.ref("hotel_housekeeping.group_clean_worker").id,
#                         )
#                     ],
#                     limit=1,
#                 )
#             )
#             if activity and clean_user:
#                 # Create Cleanliness Activity
#                 vals_activity = {
#                     "activity_id": activity.id,
#                     "housekeeper_id": clean_user.id,
#                     "clean_start_time": fields.Datetime.now(),
#                     "clean_end_time": fields.Datetime.now() + timedelta(hours=1),
#                     "today_date": datetime.today().date(),
#                 }
#                 vals.update({"activity_line_ids": [(0, 0, vals_activity)]})

#             # Create Cleanliness Service Housekeeping
#             housekeeping = self.env["hotel.housekeeping"].sudo().create(vals)
#             housekeeping._onchange_room()
#         return {
#             "name": _("Housekeeping Cleanliness Service"),
#             "res_model": "hotel.housekeeping",
#             "view_mode": "form",
#             "type": "ir.actions.act_window",
#             "res_id": housekeeping.id,
#             "target": "current",
#         }


# class HotelRoomReservationLine(models.Model):
#     _name = "hotel.room.reservation.line"
#     _description = "Hotel Room Reservation"
#     _rec_name = "room_id"

#     room_id = fields.Many2one(
#         "hotel.room", string="Room id", domain="[('is_withheld','=', False)]"
#     )
#     check_in = fields.Datetime("Check In Date", required=True)
#     check_out = fields.Datetime("Check Out Date", required=True)
#     state = fields.Selection(
#         [("assigned", "Assigned"), ("unassigned", "Unassigned")], "Room Status"
#     )
#     reservation_id = fields.Many2one("hotel.reservation", "Reservation")
#     status = fields.Selection(string="state", related="reservation_id.state")
#     reservation_line_id = fields.Many2one("hotel.reservation.line", "Reservation line")


# class HotelRoomReservationChange(models.Model):
#     _name = "reservation.room.change.history"
#     _description = "Reservation Room Change History"
#     _rec_name = "room_id"

#     change_date = fields.Datetime(string="Change Date")
#     reservation_date = fields.Datetime(string="Reservation Date")
#     old_room_id = fields.Many2one("hotel.room", string="Old Room")

#     room_id = fields.Many2one(
#         "hotel.room", string="Room", domain="[('is_withheld','=', False)]"
#     )
#     reservation_id = fields.Many2one("hotel.reservation", "Reservation")
#     reservation_line_id = fields.Many2one("hotel.reservation.line", "Reservation line")
#     is_no_calculated = fields.Boolean(string="Not calculated")
#     discount = fields.Float(string="Discount")
#     discount_type = fields.Selection(
#         string="Discount Type",
#         selection=[
#             ("no_discount", "No Discount"),
#             ("percentage", "Percentage"),
#             ("amount", "amount"),
#         ],
#     )
#     insurance = fields.Float(string="Insurance")
#     old_other_price = fields.Float(string="Old Other price")
#     other_price = fields.Float(string="Other Price")


# class FolioRoomLine(models.Model):
#     _inherit = "folio.room.line"

#     reservation_line_id = fields.Many2one("hotel.reservation.line", "Reservation Line")


# class HotelReservationHospitality(models.Model):
#     _name = "hotel.reservation.hospitality"
#     _description = "Reservation Hospitality"

#     discount_type = fields.Selection(
#         string="Discount Type",
#         selection=[
#             ("no_discount", "No Discount"),
#             ("percentage", "Percentage"),
#             ("amount", "Amount"),
#         ],
#         default="no_discount",
#     )
#     discount = fields.Float(
#         string="Discount ",
#     )
#     company_id = fields.Many2one(
#         "res.company", string="Company", default=lambda self: self.env.company
#     )
#     active = fields.Boolean(default=True)

#     @api.constrains("company_id")
#     def _check_company(self):
#         """Check company."""
#         for reservation_hospitality in self:
#             if self.search(
#                 [
#                     ("company_id", "=", reservation_hospitality.company_id.id),
#                     ("id", "!=", reservation_hospitality.id),
#                 ]
#             ):
#                 raise ValidationError(
#                     _("You should add one reservation hospitality for each company")
#                 )


# class HotelReservationSetting(models.Model):

#     _name = "hotel.reservation.setting"
#     _description = "Reservation Setting"

#     name = fields.Char(string="Name", translate=1, required=1, default="Setting")
#     hours_day = fields.Float(string="Hour that is exceeded is counted as another day")
#     company_id = fields.Many2one(
#         "res.company", string="Company", default=lambda self: self.env.company
#     )
#     active = fields.Boolean(default=True)


