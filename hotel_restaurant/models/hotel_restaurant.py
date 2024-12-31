# See LICENSE file for full copyright and licensing details.

from datetime import datetime

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HotelRestaurantTables(models.Model):

    _name = "hotel.restaurant.tables"
    _description = "Includes Hotel Restaurant Table"

    name = fields.Char("Table Number", required=True)
    capacity = fields.Integer("Capacity")


class HotelRestaurantReservation(models.Model):

    _name = "hotel.restaurant.reservation"
    _description = "Includes Hotel Restaurant Reservation"
    _rec_name = "reservation_id"

    def create_order(self):
        """
        This method is for create a new order for hotel restaurant
        reservation .when table is booked and create order button is
        clicked then this method is called and order is created.you
        can see this created order in "Orders"
        ------------------------------------------------------------
        @param self: The object pointer
        @return: new record set for hotel restaurant reservation.
        """
        reservation_order = self.env["hotel.reservation.order"]
        for record in self:
            table_ids = record.table_nos_ids.ids
            values = {
                "reservation_id": record.id,
                "order_date": record.start_date,
                "folio_id": record.folio_id.id,
                "table_nos_ids": [(6, 0, table_ids)],
                "is_folio": record.is_folio,
                "company_id": record.company_id.id,
            }
            reservation_order.create(values)
        self.write({"state": "order"})
        return True

    @api.onchange("customer_id")
    def _onchange_partner_id(self):
        """
        When Customer name is changed respective adress will display
        in Adress field
        @param self: object pointer
        """
        if not self.customer_id:
            self.partner_address_id = False
        else:
            addr = self.customer_id.address_get(["default"])
            self.partner_address_id = addr["default"]

    def action_set_to_draft(self):
        """
        This method is used to change the state
        to draft of the hotel restaurant reservation
        --------------------------------------------
        @param self: object pointer
        """
        self.write({"state": "draft"})

    def table_reserved(self):
        """
        when CONFIRM BUTTON is clicked this method is called for
        table reservation
        @param self: The object pointer
        @return: change a state depending on the condition
        """

        for reservation in self:
            if not reservation.table_nos_ids:
                raise ValidationError(_("Please Select Tables For Reservation"))
            reservation._cr.execute(
                "select count(*) from "
                "hotel_restaurant_reservation as hrr "
                "inner join reservation_table as rt on \
                             rt.reservation_table_id = hrr.id "
                "where (start_date,end_date)overlaps\
                             ( timestamp %s , timestamp %s ) "
                "and hrr.id<> %s and state != 'done'"
                "and rt.name in (select rt.name from \
                             hotel_restaurant_reservation as hrr "
                "inner join reservation_table as rt on \
                             rt.reservation_table_id = hrr.id "
                "where hrr.id= %s) ",
                (
                    reservation.start_date,
                    reservation.end_date,
                    reservation.id,
                    reservation.id,
                ),
            )
            res = self._cr.fetchone()
            roomcount = res and res[0] or 0.0
            if roomcount:
                raise ValidationError(
                    _(
                        """You tried to confirm reservation """
                        """with table those already reserved """
                        """in this reservation period"""
                    )
                )
            reservation.state = "confirm"
        return True

    def table_cancel(self):
        """
        This method is used to change the state
        to cancel of the hotel restaurant reservation
        --------------------------------------------
        @param self: object pointer
        """
        self.write({"state": "cancel"})

    def table_done(self):
        """
        This method is used to change the state
        to done of the hotel restaurant reservation
        --------------------------------------------
        @param self: object pointer
        """
        self.write({"state": "done"})

    reservation_id = fields.Char("Reservation No", readonly=True, index=True)
    room_id = fields.Many2one("product.product", "Room No")
    room_ids = fields.Many2many(
        "product.product", string="Rooms", compute="_compute_rooms"
    )
    folio_id = fields.Many2one("hotel.folio", "Folio No")
    folio_ids = fields.Many2many(
        "hotel.folio", string="Folios", compute="_compute_folios"
    )
    start_date = fields.Datetime(
        "Start Time", required=True, default=lambda self: fields.Datetime.now()
    )
    end_date = fields.Datetime("End Time", required=True)
    customer_id = fields.Many2one("res.partner", "Customer Name", required=True)
    partner_address_id = fields.Many2one("res.partner", "Address")
    table_nos_ids = fields.Many2many(
        "hotel.restaurant.tables",
        "reservation_table",
        "reservation_table_id",
        "name",
        string="Table Number",
        help="Table reservation detail.",
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirm", "Confirmed"),
            ("done", "Done"),
            ("cancel", "Cancelled"),
            ("order", "Order Created"),
        ],
        "state",
        required=True,
        readonly=True,
        copy=False,
        default="draft",
    )
    is_folio = fields.Boolean("Is a Hotel Guest??")
    company_id = fields.Many2one(
        "res.company", string="Company", default=lambda self: self.env.company
    )

    @api.depends("is_folio")
    def _compute_folios(self):
        """"""
        today = datetime.today().date()
        for restaurant_order in self:
            restaurant_order.folio_ids = False
            if restaurant_order.is_folio:
                folios = (
                    restaurant_order.env["folio.room.line"]
                    .search([])
                    .filtered(lambda folio_line: folio_line.check_out.date() >= today)
                    .mapped("folio_id")
                )
                restaurant_order.folio_ids = list(set(folios.ids))

    @api.depends("folio_id")
    def _compute_rooms(self):
        """"""
        for restaurant_order in self:
            today = datetime.today().date()
            restaurant_order.room_ids = False
            room_line = restaurant_order.folio_id.room_line_ids.filtered(
                lambda folio_line: folio_line.checkout_date.date() >= today
                and not folio_line.product_id.discount
                and not folio_line.product_id.insurance
                and not folio_line.product_id.returnable
                and folio_line.product_uom_qty
            )
            if room_line:
                restaurant_order.room_ids = room_line.mapped("product_id").ids

    @api.onchange("is_folio")
    def _onchange_is_folio(self):
        if not self.is_folio:
            self.folio_id = False
            self.room_id = False

    @api.onchange("folio_id")
    def _onchange_folio_id(self):
        """
        When you change folio_id, based on that it will update
        the customer_id and room_number as well
        ---------------------------------------------------------
        @param self: object pointer
        """
        if self.folio_id:
            today = datetime.today().date()
            self.customer_id = self.folio_id.partner_id.id
            room_line = self.folio_id.room_line_ids.filtered(
                lambda folio_line: folio_line.checkout_date.date() >= today
                and not folio_line.product_id.discount
                and not folio_line.product_id.insurance
                and not folio_line.product_id.returnable
                and folio_line.product_uom_qty
            )
            if room_line:
                self.room_id = room_line[0].product_id.id

    @api.model
    def create(self, vals):
        """
        Overrides orm create method.
        @param self: The object pointer
        @param vals: dictionary of fields value.
        """
        restaurant_reservation = super(HotelRestaurantReservation, self).create(vals)
        if restaurant_reservation:
            restaurant_reservation.reservation_id = (
                self.env["ir.sequence"].next_by_code("hotel.restaurant.reservation")
                or "New"
            )
        return restaurant_reservation

    @api.constrains("start_date", "end_date")
    def _check_start_dates(self):
        """
        This method is used to validate the start_date and end_date.
        -------------------------------------------------------------
        @param self: object pointer
        @return: raise a warning depending on the validation
        """
        for hotel_restaurant in self:
            if hotel_restaurant.start_date >= hotel_restaurant.end_date:
                raise ValidationError(_("Start Date Should be less than the End Date!"))
            if hotel_restaurant.is_folio:
                line_folio = hotel_restaurant.folio_id.room_line_ids.filtered(
                    lambda room_line_id: room_line_id.product_id
                    == hotel_restaurant.room_id
                )
                if line_folio:
                    restaurant_start_date = hotel_restaurant.start_date.date()
                    restaurant_end_date = hotel_restaurant.end_date.date()
                    folio_checkin_date = line_folio.checkin_date.date()
                    folio_checkout_date = line_folio.checkout_date.date()
                    if hotel_restaurant.folio_id.reservation_id.rent == "hours":
                        restaurant_start_date = hotel_restaurant.start_date
                        restaurant_end_date = hotel_restaurant.end_date
                        folio_checkin_date = line_folio.checkin_date
                        folio_checkout_date = line_folio.checkout_date
                    if restaurant_start_date < folio_checkin_date:
                        raise ValidationError(
                            _(
                                """Start Date Should be greater """
                                """than the Folio Check-in Date!"""
                            )
                        )

                    if restaurant_end_date > folio_checkout_date:
                        raise ValidationError(
                            _("End Date Should be less than the Folio Check-out Date!")
                        )


class HotelRestaurantKitchenOrderTickets(models.Model):

    _name = "hotel.restaurant.kitchen.order.tickets"
    _description = "Includes Hotel Restaurant Order"
    _rec_name = "order_number"

    order_number = fields.Char("Order Number", readonly=True)
    reservation_number = fields.Char("Reservation Number")
    kot_date = fields.Datetime("Date")
    room_no = fields.Char("Room No", readonly=True)
    waiter_name = fields.Char("Waiter Name", readonly=True)
    table_nos_ids = fields.Many2many(
        "hotel.restaurant.tables",
        "restaurant_kitchen_order_rel",
        "table_no",
        "name",
        "Table Number",
        help="Table reservation detail.",
    )
    kot_list_ids = fields.One2many(
        "hotel.restaurant.order.list",
        "kot_order_id",
        "Order List",
        help="Kitchen order list",
    )


class HotelRestaurantOrder(models.Model):

    _name = "hotel.restaurant.order"
    _description = "Includes Hotel Restaurant Order"
    _rec_name = "order_no"

    @api.depends(
        "order_list_ids", "order_list_ids.tax_ids", "order_list_ids.price_subtotal"
    )
    def _compute_amount_all_total(self):
        """
        amount_subtotal and amount_total will display on change of order_list_ids
        ---------------------------------------------------------------------
        @param self: object pointer
        """

        for sale in self:
            sale.amount_subtotal = sum(
                line.price_subtotal for line in sale.order_list_ids
            )
            taxes_amount = 0
            for order_list in sale.order_list_ids:
                taxes = order_list.tax_ids.compute_all(
                    order_list.item_rate,
                    order_list.menucard_id.currency_id,
                    order_list.item_qty,
                    product=order_list.menucard_id.product_id,
                    partner=sale.customer_id,
                )
                taxes_amount += sum(
                    tax.get("amount", 0.0) for tax in taxes.get("taxes", [])
                )
            sale.tax = taxes_amount
            sale.amount_total = sale.amount_subtotal + sale.tax

    def done_cancel(self):
        """
        This method is used to change the state
        to cancel of the hotel restaurant order
        ----------------------------------------
        @param self: object pointer
        """
        self.write({"state": "cancel"})

    def set_to_draft(self):
        """
        This method is used to change the state
        to draft of the hotel restaurant order
        ----------------------------------------
        @param self: object pointer
        """
        self.write({"state": "draft"})

    def generate_kot(self):
        """
        This method create new record for hotel restaurant order list.
        @param self: The object pointer
        @return: new record set for hotel restaurant order list.
        """
        res = []
        order_tickets_obj = self.env["hotel.restaurant.kitchen.order.tickets"]
        restaurant_order_list_obj = self.env["hotel.restaurant.order.list"]
        for order in self:
            if not order.order_list_ids:
                raise ValidationError(_("Please Give an Order"))
            if not order.table_nos_ids:
                raise ValidationError(_("Please Assign a Table"))
            table_ids = order.table_nos_ids.ids
            kot_data = order_tickets_obj.create(
                {
                    "order_number": order.order_no,
                    "kot_date": order.o_date,
                    "room_no": order.room_id.name,
                    "waiter_name": order.waiter_id.name,
                    "table_nos_ids": [(6, 0, table_ids)],
                }
            )

            for order_line in order.order_list_ids:
                o_line = {
                    "kot_order_id": kot_data.id,
                    "menucard_id": order_line.menucard_id.id,
                    "item_qty": order_line.item_qty,
                    "item_rate": order_line.item_rate,
                }
                restaurant_order_list_obj.create(o_line)
                res.append(order_line.id)
            order.update(
                {
                    "kitchen": kot_data.id,
                    "rest_item_id": [(6, 0, res)],
                    "state": "order",
                }
            )
        return True

    order_no = fields.Char("Order Number", readonly=True)
    o_date = fields.Datetime(
        "Order Date", required=True, default=lambda self: fields.Datetime.now()
    )
    room_id = fields.Many2one("product.product", "Room No")
    room_ids = fields.Many2many(
        "product.product", string="Rooms", compute="_compute_rooms"
    )
    folio_id = fields.Many2one("hotel.folio", "Folio No")
    folio_ids = fields.Many2many(
        "hotel.folio", string="Folios", compute="_compute_folios"
    )
    waiter_id = fields.Many2one("res.partner", "Waiter")
    table_nos_ids = fields.Many2many(
        "hotel.restaurant.tables",
        "restaurant_table_order_rel",
        "table_no",
        "name",
        "Table Number",
    )
    order_list_ids = fields.One2many(
        "hotel.restaurant.order.list", "restaurant_order_id", "Order List"
    )
    tax = fields.Float("Tax (%) ", compute="_compute_amount_all_total")
    amount_subtotal = fields.Float(
        compute="_compute_amount_all_total", string="Subtotal"
    )
    amount_total = fields.Float(compute="_compute_amount_all_total", string="Total")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("order", "Order Created"),
            ("done", "Done"),
            ("cancel", "Cancelled"),
        ],
        "State",
        required=True,
        readonly=True,
        copy=False,
        default="draft",
    )
    is_folio = fields.Boolean(
        "Is a Hotel Guest??", help="is customer reside in hotel or not"
    )
    customer_id = fields.Many2one("res.partner", "Customer Name", required=True)
    kitchen = fields.Integer("Kitchen")
    rest_item_id = fields.Many2many(
        "hotel.restaurant.order.list",
        "restaurant_kitchen_rel",
        "restau_id",
        "kit_id",
        "Rest",
    )
    company_id = fields.Many2one(
        "res.company", string="Company", default=lambda self: self.env.company
    )

    @api.depends("is_folio")
    def _compute_folios(self):
        """Calculate folios"""
        today = datetime.today().date()
        for restaurant_order in self:
            restaurant_order.folio_ids = False
            if restaurant_order.is_folio:
                folios = (
                    restaurant_order.env["folio.room.line"]
                    .search([])
                    .filtered(lambda folio_line: folio_line.check_out.date() >= today)
                    .mapped("folio_id")
                )
                restaurant_order.folio_ids = list(set(folios.ids))

    @api.depends("folio_id")
    def _compute_rooms(self):
        """Calculate Rooms"""
        for restaurant_order in self:
            today = datetime.today().date()
            restaurant_order.room_ids = False
            room_line = restaurant_order.folio_id.room_line_ids.filtered(
                lambda folio_line: folio_line.checkout_date.date() >= today
                and not folio_line.product_id.discount
                and not folio_line.product_id.insurance
                and not folio_line.product_id.returnable
                and folio_line.product_uom_qty
            )
            if room_line:
                restaurant_order.room_ids = room_line.mapped("product_id").ids

    @api.model
    def create(self, vals):
        """
        Overrides orm create method.
        @param self: The object pointer
        @param vals: dictionary of fields value.
        """
        restaurant_order = super(HotelRestaurantOrder, self).create(vals)
        if restaurant_order:
            restaurant_order.order_no = (
                self.env["ir.sequence"].next_by_code("hotel.restaurant.order") or "New"
            )
        return restaurant_order

    @api.onchange("is_folio")
    def _onchange_is_folio(self):
        if not self.is_folio:
            self.folio_id = False
            self.room_id = False

    @api.onchange("folio_id")
    def _onchange_folio_id(self):
        """
        When you change folio_id, based on that it will update
        the customer_id and room_number as well
        ---------------------------------------------------------
        @param self: object pointer
        """
        if self.folio_id:
            today = datetime.today().date()
            self.customer_id = self.folio_id.partner_id.id
            room_line = self.folio_id.room_line_ids.filtered(
                lambda folio_line: folio_line.checkout_date.date() >= today
                and not folio_line.product_id.discount
                and not folio_line.product_id.insurance
                and not folio_line.product_id.returnable
                and folio_line.product_uom_qty
            )
            if room_line:
                self.room_id = room_line[0].product_id.id

    def generate_kot_update(self):
        """
        This method update record for hotel restaurant order list.
        ----------------------------------------------------------
        @param self: The object pointer
        @return: update record set for hotel restaurant order list.
        """
        order_tickets_obj = self.env["hotel.restaurant.kitchen.order.tickets"]
        rest_order_list_obj = self.env["hotel.restaurant.order.list"]
        for order in self:
            line_data = {
                "order_number": order.order_no,
                "kot_date": fields.Datetime.to_string(fields.datetime.now()),
                "room_no": order.room_id.name,
                "waiter_name": order.waiter_id.name,
                "table_nos_ids": [(6, 0, order.table_nos_ids.ids)],
            }
            kot_id = order_tickets_obj.browse(self.kitchen)
            kot_id.write(line_data)
            for order_line in order.order_list_ids:
                if order_line.id not in order.rest_item_id.ids:
                    kot_data = order_tickets_obj.create(line_data)
                    order.kitchen = kot_data.id
                    o_line = {
                        "kot_order_id": kot_data.id,
                        "menucard_id": order_line.menucard_id.id,
                        "item_qty": order_line.item_qty,
                        "item_rate": order_line.item_rate,
                    }
                    order.rest_item_id = [(4, order_line.id)]
                    rest_order_list_obj.create(o_line)
        return True

    def done_order_kot(self):
        """
        This method is used to change the state
        to done of the hotel restaurant order
        ----------------------------------------
        @param self: object pointer
        """
        hsl_obj = self.env["hotel.service.line"]
        so_line_obj = self.env["sale.order.line"]
        for order_obj in self:
            for order in order_obj.order_list_ids:
                if order_obj.folio_id:
                    values = {
                        "order_id": order_obj.folio_id.order_id.id,
                        "name": order.menucard_id.name,
                        "product_id": order.menucard_id.product_id.id,
                        "product_uom": order.menucard_id.uom_id.id,
                        "product_uom_qty": order.item_qty,
                        "tax_id": order.tax_ids.ids,
                        "price_unit": order.item_rate,
                        "price_subtotal": order.price_subtotal,
                    }
                    sol_rec = so_line_obj.sudo().create(values)
                    hsl_obj.sudo().create(
                        {
                            "folio_id": order_obj.folio_id.id,
                            "service_line_id": sol_rec.id,
                        }
                    )
                    order_obj.folio_id.sudo().write(
                        {"hotel_restaurant_orders_ids": [(4, order_obj.id)]}
                    )
            self.write({"state": "done"})
        return True


class HotelReservationOrder(models.Model):

    _name = "hotel.reservation.order"
    _description = "Reservation Order"
    _rec_name = "order_number"

    @api.depends(
        "order_list_ids", "order_list_ids.tax_ids", "order_list_ids.price_subtotal"
    )
    def _compute_amount_all_total(self):
        """
        amount_subtotal and amount_total will display on change of order_list_ids
        ---------------------------------------------------------------------
        @param self: object pointer
        """
        for sale in self:
            sale.amount_subtotal = sum(
                line.price_subtotal for line in sale.order_list_ids
            )
            taxes_amount = 0
            for order_list in sale.order_list_ids:
                taxes = order_list.tax_ids.compute_all(
                    order_list.item_rate,
                    order_list.menucard_id.currency_id,
                    order_list.item_qty,
                    product=order_list.menucard_id.product_id,
                    partner=False,
                )
                taxes_amount += sum(
                    tax.get("amount", 0.0) for tax in taxes.get("taxes", [])
                )
            sale.tax = taxes_amount
            sale.amount_total = sale.amount_subtotal + sale.tax

    def reservation_generate_kot(self):
        """
        This method create new record for hotel restaurant order list.
        --------------------------------------------------------------
        @param self: The object pointer
        @return: new record set for hotel restaurant order list.
        """
        res = []
        order_tickets_obj = self.env["hotel.restaurant.kitchen.order.tickets"]
        rest_order_list_obj = self.env["hotel.restaurant.order.list"]
        for order in self:
            if not order.order_list_ids:
                raise ValidationError(_("Please Give an Order"))
            table_ids = order.table_nos_ids.ids
            line_data = {
                "order_number": order.order_number,
                "reservation_number": order.reservation_id.reservation_id,
                "kot_date": order.order_date,
                "waiter_name": order.waitername.name,
                "table_nos_ids": [(6, 0, table_ids)],
            }
            kot_data = order_tickets_obj.create(line_data)
            for order_line in order.order_list_ids:
                o_line = {
                    "kot_order_id": kot_data.id,
                    "menucard_id": order_line.menucard_id.id,
                    "item_qty": order_line.item_qty,
                    "item_rate": order_line.item_rate,
                }
                rest_order_list_obj.create(o_line)
                res.append(order_line.id)
            order.update(
                {"kitchen": kot_data.id, "rests_ids": [(6, 0, res)], "state": "order"}
            )
        return res

    def reservation_update_kot(self):
        """
        This method update record for hotel restaurant order list.
        ----------------------------------------------------------
        @param self: The object pointer
        @return: update record set for hotel restaurant order list.
        """
        order_tickets_obj = self.env["hotel.restaurant.kitchen.order.tickets"]
        rest_order_list_obj = self.env["hotel.restaurant.order.list"]
        for order in self:
            table_ids = order.table_nos_ids.ids
            line_data = {
                "order_number": order.order_number,
                "reservation_number": order.reservation_id.reservation_id,
                "kot_date": fields.Datetime.to_string(fields.datetime.now()),
                "waiter_name": order.waitername.name,
                "table_nos_ids": [(6, 0, table_ids)],
            }
            kot_id = order_tickets_obj.browse(self.kitchen)
            kot_id.write(line_data)
            for order_line in order.order_list_ids:
                if order_line not in order.rests_ids.ids:
                    kot_data = order_tickets_obj.create(line_data)
                    o_line = {
                        "kot_order_id": kot_data.id,
                        "menucard_id": order_line.menucard_id.id,
                        "item_qty": order_line.item_qty,
                        "item_rate": order_line.item_rate,
                    }
                    order.update(
                        {"kitchen": kot_data.id, "rests_ids": [(4, order_line.id)]}
                    )
                    rest_order_list_obj.create(o_line)
        return True

    def done_kot(self):
        """
        This method is used to change the state
        to done of the hotel reservation order
        ----------------------------------------
        @param self: object pointer
        """
        hsl_obj = self.env["hotel.service.line"]
        so_line_obj = self.env["sale.order.line"]
        for res_order in self:
            for order in res_order.order_list_ids:
                if res_order.folio_id:
                    values = {
                        "order_id": res_order.folio_id.order_id.id,
                        "name": order.menucard_id.name,
                        "product_id": order.menucard_id.product_id.id,
                        "product_uom_qty": order.item_qty,
                        "price_unit": order.item_rate,
                        "tax_id": order.tax_ids.ids,
                        "price_subtotal": order.price_subtotal,
                    }
                    sol_rec = so_line_obj.sudo().create(values)
                    hsl_obj.sudo().create(
                        {
                            "folio_id": res_order.folio_id.id,
                            "service_line_id": sol_rec.id,
                        }
                    )
                    res_order.folio_id.sudo().write(
                        {"hotel_reservation_orders_ids": [(4, res_order.id)]}
                    )
            res_order.reservation_id.write({"state": "done"})
        self.write({"state": "done"})
        return True

    order_number = fields.Char("Order No", readonly=True)
    reservation_id = fields.Many2one("hotel.restaurant.reservation", "Reservation No")
    order_date = fields.Datetime(
        "Date", required=True, default=lambda self: fields.Datetime.now()
    )
    waitername = fields.Many2one("res.partner", "Waiter Name")
    table_nos_ids = fields.Many2many(
        "hotel.restaurant.tables",
        "temp_table4",
        "table_no",
        "name",
        "Table Number",
    )
    order_list_ids = fields.One2many(
        "hotel.restaurant.order.list", "reservation_order_id", "Order List"
    )
    tax = fields.Float("Tax (%) ", compute="_compute_amount_all_total")
    amount_subtotal = fields.Float(
        compute="_compute_amount_all_total", string="Subtotal"
    )
    amount_total = fields.Float(compute="_compute_amount_all_total", string="Total")
    kitchen = fields.Integer("Kitchen Id")
    rests_ids = fields.Many2many(
        "hotel.restaurant.order.list",
        "reserv_id",
        "kitchen_id",
        "res_kit_ids",
        "Rest",
    )
    state = fields.Selection(
        [("draft", "Draft"), ("order", "Order Created"), ("done", "Done")],
        "State",
        required=True,
        readonly=True,
        default="draft",
    )
    folio_id = fields.Many2one("hotel.folio", "Folio No")
    is_folio = fields.Boolean(
        "Is a Hotel Guest??", help="is customer reside in hotel or not"
    )
    company_id = fields.Many2one(
        "res.company", string="Company", default=lambda self: self.env.company
    )

    @api.model
    def create(self, vals):
        """
        Overrides orm create method.
        @param self: The object pointer
        @param vals: dictionary of fields value.
        """
        reservation_order = super(HotelReservationOrder, self).create(vals)
        if reservation_order:
            reservation_order.order_number = (
                self.env["ir.sequence"].next_by_code("hotel.reservation.order") or "New"
            )
        return reservation_order


class HotelRestaurantOrderList(models.Model):

    _name = "hotel.restaurant.order.list"
    _description = "Includes Hotel Restaurant Order"

    @api.depends("item_qty", "item_rate")
    def _compute_price_subtotal(self):
        """
        price_subtotal will display on change of item_rate
        --------------------------------------------------
        @param self: object pointer
        """
        for line in self:
            line.price_subtotal = line.item_rate * int(line.item_qty)

    def _get_computed_taxes(self):
        self.ensure_one()
        if self.menucard_id.product_id.taxes_id:
            tax_ids = self.menucard_id.product_id.taxes_id.filtered(
                lambda tax: tax.company_id == self.company_id
            )
        else:
            tax_ids = self.env["account.tax"]
        if not tax_ids:
            tax_ids = self.company_id.account_sale_tax_id
        if self.company_id and tax_ids:
            tax_ids = tax_ids.filtered(lambda tax: tax.company_id == self.company_id)
        return tax_ids

    @api.onchange("menucard_id")
    def _onchange_item_name(self):
        """
        item rate will display on change of item name
        ---------------------------------------------
        @param self: object pointer
        """
        self.item_rate = self.menucard_id.list_price
        if self.restaurant_order_id:
            self.company_id = self.restaurant_order_id.company_id.id
        if self.reservation_order_id:
            self.company_id = self.reservation_order_id.company_id.id
        taxes = self._get_computed_taxes()
        self.tax_ids = taxes

    restaurant_order_id = fields.Many2one("hotel.restaurant.order", "Restaurant Order")
    reservation_order_id = fields.Many2one(
        "hotel.reservation.order", "Reservation Order"
    )
    kot_order_id = fields.Many2one(
        "hotel.restaurant.kitchen.order.tickets", "Kitchen Order Tickets"
    )
    menucard_id = fields.Many2one("hotel.menucard", "Item Name", required=True)
    item_qty = fields.Integer("Qty", required=True, default=1)
    item_rate = fields.Float("Rate")
    price_subtotal = fields.Float(compute="_compute_price_subtotal", string="Subtotal")
    tax_ids = fields.Many2many(
        "account.tax",
        string="Taxes",
        context={"active_test": False},
        check_company=True,
        help="Taxes that apply on the base amount",
    )

    company_id = fields.Many2one("res.company")
