from datetime import date

from lxml import etree

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ShippingOrder(models.Model):
    _name = "shipping.order"
    _description = "Shipping Orders"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(string="Order Number", readonly=1)
    clearance_request_id = fields.Many2one(
        "clearance.request",
        string="Clearance",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    shipping_order_id = fields.Many2one("shipping.order", string="Shipping Order")
    request_type = fields.Selection(
        related="clearance_request_id.request_type", store=1, string="Request Type"
    )
    transport_type = fields.Selection(
        string="Transport type",
        selection=[
            ("warehouse", "Yard"),
            ("customer", "Customer site"),
            ("other", "Other site"),
            ("empty", "Return empty"),
        ],
        default="warehouse",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    company_id = fields.Many2one(
        "res.company",
        "Company",
        default=lambda self: self.env.company,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    line_ids = fields.One2many(
        "shipping.order.line",
        "shipping_order_id",
        string="Shipping Order Line",
        readonly=True,
        states={"draft": [("readonly", False)], "done": [("readonly", False)]},
    )
    used_goods = fields.Many2many(
        "clearance.request.shipment.type", string="Goods", compute="_compute_used_goods"
    )
    shipment_type = fields.Selection(
        related="clearance_request_id.shipment_type", store=1
    )
    meeting_count = fields.Integer(
        compute="_compute_meeting_count", help="Meeting Count"
    )
    payments_covenant_number = fields.Integer(
        string="Payments Covenant number", compute="_compute_payments_covenant"
    )
    payments_covenant_ids = fields.One2many(
        "account.payment",
        "shipping_order_id",
        string="Payments Covenant",
        readonly=True,
        domain=[("is_reward_drivers", "=", False)],
    )
    payments_drivers_number = fields.Integer(
        string="Payments Drivers number", compute="_compute_payments_drivers"
    )
    partner_id = fields.Many2one(
        "res.partner",
        string="Partner",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    payments_drivers_ids = fields.One2many(
        "account.payment",
        "shipping_order_id",
        string="Payments Drivers",
        readonly=True,
        domain=[("is_reward_drivers", "=", True)],
    )
    create_date = fields.Datetime("Shipping Order Date")
    shipping_order_number = fields.Integer(
        string="Shipping Orders number",
        compute="_compute_shipping_orders",
        compute_sudo=True,
    )
    is_paid = fields.Boolean("Is Paid", compute="_compute_is_paid", store=1)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("done", "Done"),
            ("canceled", "Canceled"),
            ("closed", "Closed"),
        ],
        default="draft",
        string="State",
        tracking=True,
    )
    is_set_to_draft = fields.Boolean(
        compute="_compute_set_to_draft", string="Set To Draft"
    )
    statement_number = fields.Char(
        string="Statement Number",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    shipping_number = fields.Char(
        string="BL Number", readonly=True, states={"draft": [("readonly", False)]}
    )
    service_ids = fields.Many2many("product.product", compute="_compute_service_ids")

    # ------------------------------------------------------------
    # Constraints methods
    # ------------------------------------------------------------
    @api.constrains("transport_type", "shipping_order_id")
    def _check_transport_type(self):
        for shipping_order in self:
            if (
                shipping_order.shipping_order_id
                and shipping_order.shipping_order_id.transport_type == "warehouse"
                and shipping_order.transport_type == "warehouse"
            ):
                raise ValidationError(_("You Can't choose a yard"))
            if shipping_order.line_ids.filtered(
                lambda line: line.route_id.transport_type
                != shipping_order.transport_type
            ):
                raise ValidationError(
                    _(
                        "Shipping order transport type is different"
                        " to transport types of containers routes"
                    )
                )

    # ------------------------------------------------------------
    # Compute methods
    # ------------------------------------------------------------
    @api.depends("state", "line_ids", "line_ids.payment_reward_id")
    def _compute_set_to_draft(self):
        for shipping in self:
            shipping.is_set_to_draft = False
            lines = shipping.line_ids.filtered(lambda line: not line.payment_reward_id)
            if lines and shipping.state == "done":
                shipping.is_set_to_draft = True

    @api.depends("shipping_order_id")
    def _compute_shipping_orders(self):
        """Calculate shipping order related to yar shipping orders."""
        for request in self:
            request.shipping_order_number = request.search_count(
                [("shipping_order_id", "=", request.id)]
            )

    @api.depends("line_ids", "line_ids.payment_reward_id", "payments_drivers_number")
    def _compute_is_paid(self):
        for shipping in self:
            shipping.is_paid = (
                True
                if (
                    shipping.line_ids
                    and len(
                        shipping.line_ids.filtered(lambda line: line.payment_reward_id)
                    )
                )
                else False
            )

    @api.depends("clearance_request_id", "line_ids.goods_id", "state", "transport_type")
    def _compute_used_goods(self):
        """Calculate orders."""
        for shipping in self:
            shipping.used_goods = False
            used_goods = shipping.clearance_request_id.statement_line_ids.ids

            if (
                shipping.shipping_order_id
                and shipping.shipping_order_id.transport_type == "warehouse"
            ):
                related_shipment = shipping.env["shipping.order"].search(
                    [
                        ("shipping_order_id", "=", shipping.shipping_order_id.id),
                        ("state", "!=", "canceled"),
                    ]
                )
                used_goods = [
                    good
                    for good in shipping.shipping_order_id.mapped(
                        "line_ids.goods_id"
                    ).ids
                    if good not in (related_shipment.mapped("line_ids.goods_id").ids)
                ]
            elif (
                len(shipping.clearance_request_id.order_ids)
                and shipping.transport_type != "empty"
            ):
                used_goods = [
                    good
                    for good in used_goods
                    if good
                    not in (
                        shipping.clearance_request_id.order_ids.mapped(
                            "line_ids.goods_id"
                        ).ids
                        + shipping.mapped("line_ids.goods_id").ids
                    )
                ]
            elif shipping.transport_type == "empty":
                # calculte uses good for return empty ( show all goods)
                used_goods = [
                    good
                    for good in used_goods
                    if good
                    not in (
                        shipping.clearance_request_id.order_ids.filtered(
                            lambda order: order.transport_type == "empty"
                            and order.state != "canceled"
                        )
                        .mapped("line_ids.goods_id")
                        .ids
                        + shipping.mapped("line_ids.goods_id").ids
                    )
                ]

            shipping.used_goods = used_goods

    def _compute_meeting_count(self):
        if self.ids:
            meeting_data = (
                self.env["calendar.event"]
                .sudo()
                .read_group(
                    [("shipping_order_id", "in", self.ids)],
                    ["shipping_order_id"],
                    ["shipping_order_id"],
                )
            )
            mapped_data = {
                m["shipping_order_id"][0]: m["shipping_order_id_count"]
                for m in meeting_data
            }
        else:
            mapped_data = dict()
        for shipping in self:
            shipping.meeting_count = mapped_data.get(shipping.id, 0)

    @api.depends("payments_covenant_ids")
    def _compute_payments_covenant(self):
        """Calculate payments."""
        for request in self:
            request.payments_covenant_number = len(request.payments_covenant_ids)

    @api.depends("payments_drivers_ids")
    def _compute_payments_drivers(self):
        """Calculate payments drivers."""
        for request in self:
            request.payments_drivers_number = len(request.payments_drivers_ids)

    @api.depends("transport_type")
    def _compute_service_ids(self):
        for order in self:
            order.service_ids = (
                order.env["clearance.product.invoice.setting"]
                .search([("company_id", "=", self.company_id.id)], limit=1)
                .mapped("services_ids")
            )

    # ------------------------------------------------------
    # ORM Methods
    # ------------------------------------------------------
    def _create_sequence(self):
        """Create shipping order sequence by company."""
        self.company_id.sudo().shipping_order_sequence_id = (
            self.env["ir.sequence"]
            .sudo()
            .create(
                {
                    "name": "Shipping Order " + self.company_id.name,
                    "padding": 5,
                    "code": "res.company",
                }
            )
            .id
        )

    def _check_goods_availability(
        self, shipping_order_warehouse, clearance, transport_type
    ):
        """Return availability goods from shipping order or clearance."""
        used_goods = clearance.statement_line_ids.ids
        if shipping_order_warehouse:

            used_goods = [
                good
                for good in shipping_order_warehouse.mapped("line_ids.goods_id").ids
                if good
                not in self.search(
                    [
                        ("shipping_order_id", "=", shipping_order_warehouse.id),
                        ("state", "!=", "canceled"),
                    ]
                )
                .mapped("line_ids.goods_id")
                .ids
            ]
        else:
            if transport_type == "empty":
                # check avaibility of goos for empty return
                used_goods = [
                    good
                    for good in used_goods
                    if good
                    not in (
                        clearance.order_ids.filtered(
                            lambda order: order.transport_type == "empty"
                            and order.state != "canceled"
                        )
                        .mapped("line_ids.goods_id")
                        .ids
                    )
                ]
            else:
                if len(clearance.order_ids):
                    used_goods = [
                        good
                        for good in used_goods
                        if good
                        not in clearance.order_ids.mapped("line_ids.goods_id").ids
                    ]
        return used_goods

    @api.model
    def create(self, values):
        clearance = self.env["clearance.request"].browse(
            values.get("clearance_request_id")
        )
        shipping_order_warehouse = False
        if self.env.context.get("default_shipping_order_id", False):
            shipping_order_warehouse = self.browse(
                self.env.context.get("default_shipping_order_id", False)
            )
        used_goods = self._check_goods_availability(
            shipping_order_warehouse, clearance, values.get("transport_type")
        )
        if not used_goods and clearance.shipment_type in ["fcl", "lcl", "other"]:
            raise ValidationError(_("There is no goods left"))
        else:
            shipping_order = super(ShippingOrder, self).create(values)
            if (
                shipping_order
                and not shipping_order.company_id.shipping_order_sequence_id
            ):
                shipping_order._create_sequence()
            shipping_order.name = (
                shipping_order.company_id.shipping_order_sequence_id.next_by_id()
            )
            return shipping_order

    # ------------------------------------------------------
    # Business Methods
    # ------------------------------------------------------

    @api.model
    def fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        """fields_view_get to remove dit and create ."""
        res = super(ShippingOrder, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu
        )
        if (
            self.env.context.get("no_create_edit")
            or self.env.context.get("clearance_request_state") == "close"
        ):
            doc = etree.XML(res["arch"])
            for node in doc.xpath("//tree"):
                node.set("create", "0")
                node.set("edit", "0")
            for node in doc.xpath("//form"):
                node.set("create", "0")
                # node.set("edit", "0")
            res["arch"] = etree.tostring(doc, encoding="unicode")
        return res

    def shipping_order_view(self):
        """Get shipping orders for this object."""
        action = (
            self.env.ref("transportation.shipping_order_action_warehouse")
            .sudo()
            .read()[0]
        )
        action["context"] = {
            "default_clearance_request_id": self.clearance_request_id.id,
            "default_company_id": self.company_id.id,
            "clearance_request_state": self.clearance_request_id.state,
            "default_shipping_order_id": self.id,
            "default_transport_type": "customer",
            "default_partner_id": self.partner_id.id if self.partner_id else False,
            "default_statement_number": self.statement_number,
            "default_shipping_number": self.shipping_number,
        }
        return action

    def action_makeMeeting(self):
        """This opens Meeting's calendar view to schedule meeting on current planning
        @return: Dictionary value for created Meeting view
        """
        self.ensure_one()
        partners = self.env.user.partner_id

        category = self.env.ref("transportation.categ_meet_appointment_reservation")
        res = self.env["ir.actions.act_window"]._for_xml_id(
            "calendar.action_calendar_event"
        )
        res["context"] = {
            "default_partner_ids": partners.ids,
            "default_user_id": self.env.uid,
            "default_name": _("Shipping Order ") + self.name,
            "default_categ_ids": category and [category.id] or False,
            "default_shipping_order_id": self.id,
        }
        res["domain"] = [("shipping_order_id", "=", self.id)]
        return res

    def payment_orders_covenant(self):
        """Get payments for this object."""

        financial_settings = self.env["transportation.financial.settings"].search(
            [("company_id", "=", self.company_id.id)], limit=1
        )
        action = self.env.ref("account.action_account_payments").sudo().read()[0]
        action["domain"] = [("id", "in", self.payments_covenant_ids.ids)]
        action["context"] = {
            "default_clearance_request_id": self.clearance_request_id.id,
            "default_shipping_order_id": self.id,
            "default_journal_id": financial_settings.journal_id.id
            if financial_settings
            else False,
            "default_partner_type": "supplier",
            "default_payment_type": "outbound",
        }

        return action

    def payment_drivers(self):
        """Get payments for drivers."""
        action = self.env.ref("account.action_account_payments").sudo().read()[0]
        action["domain"] = [("id", "in", self.payments_drivers_ids.ids)]
        action["context"] = {
            "default_is_reward_drivers": True,
        }

        action["views"] = [
            (
                self.env.ref(
                    "transportation.view_account_payment_tree_reward_transportation"
                ).id,
                "tree",
            ),
            (
                self.env.ref("account.view_account_payment_form").id,
                "form",
            ),
        ]
        return action

    def get_route_amounts(self, route, date):
        """Get route minimum, parcel and container amount."""
        minimum_amount = route.minimum_amount
        parcel_transport = route.parcel_transport
        container_transport = route.container_transport
        # get amount based on date
        route_amounts = route.line_ids.filtered(
            lambda line: line.date_from <= date <= line.date_to
        )
        if route_amounts:
            minimum_amount = route_amounts[0].minimum_amount
            parcel_transport = route_amounts[0].parcel_transport
            container_transport = route_amounts[0].container_transport
        return minimum_amount, parcel_transport, container_transport

    def create_rewards_payments(self):
        for shipping in self:
            financial_settings = self.env["transportation.financial.settings"].search(
                [("company_id", "=", shipping.company_id.id)], limit=1
            )
            today = date.today()
            for line in shipping.line_ids:
                # get minimum_amount based on route dates
                (
                    minimum_amount,
                    parcel_transport,
                    container_transport,
                ) = shipping.get_route_amounts(line.route_id, today)
                line.payment_reward_id = shipping.env["account.payment"].create(
                    {
                        "shipping_order_id": shipping.id,
                        "clearance_request_id": shipping.clearance_request_id.id,
                        "journal_id": financial_settings.journal_id.id
                        if financial_settings
                        else False,
                        "partner_type": "supplier",
                        "payment_type": "outbound",
                        "amount": minimum_amount,
                        "reward": parcel_transport
                        if line.shipping_order_id.shipment_type == "lcl"
                        else container_transport,
                        "partner_id": line.driver_id.id,
                        "shipping_line_ids": [(4, line.id)],
                        "is_reward_drivers": True,
                    }
                )
                shipping.payments_drivers_ids += line.payment_reward_id

    def create_invoice_difference_line(self, invoice, product, account):
        """Create invoice line for  transport difference route"""
        # create invoice line
        invoice_line = (
            self.env["account.move.line"]
            .with_context(check_move_validity=False)
            .create(
                {
                    "product_id": product,
                    "quantity": 1,
                    "move_id": invoice,
                    "account_id": account,
                }
            )
        )
        invoice_line._onchange_product_id()
        invoice_line._onchange_uom_id()
        return invoice_line

    def prepare_empty_invoice_vals(self, clearance):
        """Prepare vals of invoice of difference between routes prices and invoices"""
        fiscal_position = (
            self.env["account.fiscal.position"]
            .with_company(clearance.company_id)
            .get_fiscal_position(clearance.partner_id.id, delivery_id=None)
        )
        payment_term = clearance.partner_id.property_payment_term_id
        invoice_vals = {
            "ref": clearance.name,
            "invoice_origin": clearance.name,
            "move_type": "out_invoice",
            "invoice_date": fields.Date.today(),
            "company_id": clearance.company_id.id,
            "journal_id": self.env["account.journal"]
            .search(
                [("company_id", "=", clearance.company_id.id), ("type", "=", "sale")],
                limit=1,
            )
            .id,
            "partner_id": clearance.partner_id,
            "fiscal_position_id": fiscal_position,
            "currency_id": clearance.company_id.currency_id.id,
            "invoice_payment_term_id": payment_term,
            "clearance_request_id": clearance.id,
        }
        return invoice_vals

    def create_transport_invoice_difference(self, product_setting, invoice, price_unit):
        """Create invoice of difference between routes prices and invoices."""
        fiscal_position = invoice.fiscal_position_id
        accounts = False
        if fiscal_position:
            accounts = (
                product_setting.transport_product_id.product_tmpl_id.with_company(
                    self.company_id
                ).get_product_accounts(fiscal_pos=fiscal_position)
            )
        # create transport invoice line
        invoice_line = self.create_invoice_difference_line(
            invoice.id,
            product_setting.transport_product_id.id,
            accounts["income"].id
            if accounts
            else invoice.journal_id.default_account_id.id,
        )
        invoice_line.price_unit = abs(price_unit)

    def create_invoice_line(self, invoice, product, account):
        """Create invoice line for services"""
        invoice_line = (
            self.env["account.move.line"]
            .with_context(check_move_validity=False)
            .create(
                {
                    "product_id": product,
                    "quantity": 1,
                    "move_id": invoice,
                    "account_id": account,
                }
            )
        )
        invoice_line._onchange_product_id()
        invoice_line._onchange_uom_id()
        return invoice_line

    def create_service_invoice(self, service_ids, invoice):
        """Create service invoice."""
        for product in service_ids:
            fiscal_position = invoice.fiscal_position_id
            accounts = False
            if fiscal_position:
                accounts = product.product_tmpl_id.with_company(
                    self.company_id
                ).get_product_accounts(fiscal_pos=fiscal_position)
            # create transport invoice line
            self.create_invoice_line(
                invoice.id,
                product.id,
                accounts["income"].id
                if accounts
                else invoice.journal_id.default_account_id.id,
            )

    def get_routes_amounts_invoice(self, lines):
        """Get total routes prices"""
        route_prices = 0
        route_without_price = 0
        for line in lines:
            shipment_route_price = self.env[
                "clearance.request.shipment.route.price"
            ].search(
                [
                    ("route_id", "=", line.route_id.id),
                    ("date_from", "<=", line.shipping_order_id.create_date.date()),
                    ("date_to", ">=", line.shipping_order_id.create_date.date()),
                ],
                limit=1,
            )
            route_prices += shipment_route_price.amount if shipment_route_price else 0
            route_without_price += 1 if not shipment_route_price else 0
        return route_prices, route_without_price

    def action_done(self):
        if self.clearance_request_id and self.transport_type == "customer":
            product_setting = self.env["clearance.product.invoice.setting"].search(
                [("company_id", "=", self.company_id.id)], limit=1
            )
            # get total of line of transport from invoice
            invoices_transport = self.clearance_request_id.account_move_ids.mapped(
                "invoice_line_ids"
            ).filtered(
                lambda line: line.move_id.move_type == "out_invoice"
                and line.move_id.state != "cancel"
                and not line.move_id.is_warehouse_invoice
                and line.product_id == product_setting.transport_product_id
            )
            invoices_transport_amount = sum(invoices_transport.mapped("price_subtotal"))
            # get lines from done shipment orders and curren shipment
            lines = self.line_ids + self.search(
                [
                    ("clearance_request_id", "=", self.clearance_request_id.id),
                    ("state", "=", "done"),
                    ("transport_type", "=", "customer"),
                ]
            ).mapped("line_ids")
            route_prices, routes_without_price = self.get_routes_amounts_invoice(lines)
            # create invoice if there is difference between routes prices and precedent invoice
            if (
                len(invoices_transport)
                and not routes_without_price
                and route_prices != invoices_transport_amount
                and len(lines) == len(self.clearance_request_id.statement_line_ids)
            ):
                invoice_vals = self.prepare_empty_invoice_vals(
                    self.clearance_request_id
                )
                invoice = self.env["account.move"].create(invoice_vals)
                invoice._onchange_partner_id_account_invoice_pricelist()
                self.create_transport_invoice_difference(
                    product_setting, invoice, (route_prices - invoices_transport_amount)
                )
                invoice.with_context(
                    check_move_validity=False
                )._onchange_invoice_line_ids()
                invoice.with_context(check_move_validity=False)._recompute_tax_lines()
        # Check if the transportation order is created fom a warehouse transportation order
        if (
            self.clearance_request_id
            and self.transport_type == "customer"
            and self.shipping_order_id.transport_type == "warehouse"
        ):
            # get the services of the warehouse transportation order
            service_ids = self.shipping_order_id.line_ids.mapped("service_id")
            # if the warehouse transportation order has services we are going to add an invoice with them
            if service_ids:
                service_invoice_vals = self.prepare_empty_invoice_vals(
                    self.clearance_request_id
                )
                invoice = self.env["account.move"].create(service_invoice_vals)
                invoice._onchange_partner_id_account_invoice_pricelist()
                # Add line in the invoice for each service
                self.create_service_invoice(service_ids, invoice)
                invoice.with_context(
                    check_move_validity=False
                )._onchange_invoice_line_ids()
                invoice.with_context(check_move_validity=False)._recompute_tax_lines()
        # change state
        self.state = "done"

    def action_closed(self):
        self.state = "closed"

    def action_cancel(self):
        for order in self:
            order.state = "canceled"
            # get related orders to cancel them
            orders = order.env["shipping.order"].search(
                [("shipping_order_id", "=", order.id)]
            )
            orders.write({"state": "canceled"})
            orders += order
            # cancel shipping order related draft payments
            payments = self.env["account.payment"].search(
                [("shipping_order_id", "in", orders.ids)]
            )
            draft_payments_ids = payments.filtered(
                lambda payment: payment.state == "draft"
            )
            draft_payments_ids.action_cancel()
            # cancel shipping order related not draft payments
            not_draft_payments = payments.filtered(
                lambda payment: payment.state not in ["draft", "cancel"]
            )
            not_draft_payments.action_draft()
            not_draft_payments.action_cancel()

    def set_to_draft(self):
        return self.write({"state": "draft"})


class ShippingOrderLine(models.Model):
    _name = "shipping.order.line"
    _description = "Shipping Order Line"
    _rec_name = "goods_id"

    number = fields.Char("Number")
    shipping_order_id = fields.Many2one("shipping.order", string="Shipping Order")
    shipping_datetime = fields.Datetime("Date and Time", required=1)
    goods_id = fields.Many2one("clearance.request.shipment.type", string="Good")
    vehicle_id = fields.Many2one("fleet.vehicle", string="Vehicle")
    driver_id = fields.Many2one("res.partner", "Driver")
    shipment_type_size_id = fields.Many2one(
        "clearance.shipment.type.size", string="Size"
    )
    type_lcl = fields.Selection(
        string="Type",
        selection=[("bale", "Bale"), ("package", "Package")],
        default="bale",
    )
    uom_id = fields.Many2one("uom.uom", "Unit of Measure")
    weight = fields.Float(string="Weight")
    container_number = fields.Char(string="Container Number")
    route_id = fields.Many2one("clearance.request.shipment.route", string="Route")
    shipment_from = fields.Char(string="From", translate=1)
    shipment_to = fields.Char(string="To", translate=1)
    delivery_date = fields.Date(string="Delivery date")
    company_id = fields.Many2one(
        "res.company", "Company", default=lambda self: self.env.company.id
    )
    location_number = fields.Char(string="Location number")
    state = fields.Selection(
        related="shipping_order_id.clearance_request_id.state", store=1
    )
    is_user_groups_only_delivery = fields.Boolean(
        string="", compute="_compute_user_groups_only_delivery"
    )
    container_category_id = fields.Many2one(
        "container.category", string="Container Category"
    )
    is_paid = fields.Boolean("Is Paid")
    payment_reward_id = fields.Many2one("account.payment", string="Payment Reward")
    confirmed = fields.Boolean("Confirmed")
    route_ids = fields.Many2many(
        "clearance.request.shipment.route", string="Routes", compute="_compute_routes"
    )
    service_id = fields.Many2one("product.product")

    @api.model
    def create(self, vals):
        """Generate number automatically unique by order line."""
        rec = super(ShippingOrderLine, self).create(vals)
        rec.number = rec._generate_sequence()
        # post msg of routes
        route = rec.env["clearance.request.shipment.route"].browse(vals.get("route_id"))
        content = _("Route : ") + str(route.name)
        rec.shipping_order_id.message_post(body=content)
        return rec

    def write(self, vals):
        # Post msg of if routes are changes
        old_route = self.route_id.name
        res = super(ShippingOrderLine, self).write(vals)
        for line in self:
            if vals.get("route_id"):
                route = line.env["clearance.request.shipment.route"].browse(
                    vals.get("route_id")
                )
                line.shipping_order_id.message_post(
                    body=_("The Route is changed from %s to %s")
                    % (old_route, route.name)
                )
        return res

    # Fonctions
    def _generate_sequence(self):
        for line in self:
            shipment = line.env["shipping.order.line"].search(
                [
                    ("id", "!=", line.id),
                    ("shipping_order_id", "=", line.shipping_order_id.id),
                ],
                order="id desc",
                limit=1,
            )
            if shipment:
                number = int(shipment.number) + 1
            else:
                number = 1
            return number

    def check_date_fleet(self, date_fleet, message):
        today = date.today()
        if date_fleet and date_fleet < today:
            raise ValidationError(
                _("Cannot print WAY BILL if the %s " + "" + " has expired:%s")
                % (message, date_fleet)
            )

    def print_payment_order_report(self):
        if self.payment_reward_id:
            return self.env.ref("account.action_report_payment_receipt").report_action(
                self.payment_reward_id
            )

    # flake8: noqa: C901
    def print_way_bill_report(self):
        self.ensure_one()
        if self.vehicle_id:
            if self.vehicle_id.driving_license_end_date:
                message = _("Driving License Expiration Date")
                self.check_date_fleet(self.vehicle_id.driving_license_end_date, message)
            if self.vehicle_id.driver_expiry_date:
                message = _("Driver Expiry Date")
                self.check_date_fleet(self.vehicle_id.driver_expiry_date, message)
            if self.vehicle_id.play_card_end_date:
                message = _("Play Card Expiration Date")
                self.check_date_fleet(self.vehicle_id.play_card_end_date, message)
            if self.vehicle_id.expiry_card_end_date:
                message = _("Expiry Card Expiration Date")
                self.check_date_fleet(self.vehicle_id.expiry_card_end_date, message)
            if self.vehicle_id.insurance_end_date:
                message = _("Insurance Expiration Date")
                self.check_date_fleet(self.vehicle_id.insurance_end_date, message)
            if self.vehicle_id.periodic_inspection_end_date:
                message = _("Periodic inspection Expiration Date")
                self.check_date_fleet(
                    self.vehicle_id.periodic_inspection_end_date, message
                )
            if self.vehicle_id.insurance_no_cargo_end_date:
                message = _("Insurance No/Cargo End Date")
                self.check_date_fleet(
                    self.vehicle_id.insurance_no_cargo_end_date, message
                )
            if self.vehicle_id.driver_license_expiry_date:
                message = _("Driver License Expiry Date")
                self.check_date_fleet(
                    self.vehicle_id.driver_license_expiry_date, message
                )
        if self.driver_id:
            driver_id = self.env["hr.employee"].search(
                [("address_home_id", "=", self.driver_id.id)], limit=1
            )
            if driver_id.insurance_end_date:
                message = _("Insurance Expiration Date")
                self.check_date_fleet(driver_id.insurance_end_date, message)
            if driver_id.driving_license_end_date:
                message = _("Driving license Expiration Date")
                self.check_date_fleet(driver_id.driving_license_end_date, message)
            if driver_id.port_licence_end_date:
                message = _("Port Licence Expiration Date")
                self.check_date_fleet(driver_id.port_licence_end_date, message)
            if driver_id.play_card_end_date:
                message = _("Drive Play Card Expiration Date")
                self.check_date_fleet(driver_id.play_card_end_date, message)
            if driver_id.health_certificate_end_date:
                message = _("Health certificate Expiration Date")
                self.check_date_fleet(driver_id.health_certificate_end_date, message)
        # confirm shipping order line
        if not self.confirmed:
            self.confirmed = True
        # create payment reward
        if not self.payment_reward_id:
            self.create_reward_payment()
        return self.env.ref("transportation.report_way_bill_line").report_action(self)

    def _compute_user_groups_only_delivery(self):
        """Calculate user groups delivery."""
        for line in self:
            line.is_user_groups_only_delivery = False
            if line.env.user.has_group(
                "transportation.group_delivery_responsible"
            ) and not line.env.user.has_group(
                "transportation.group_transportation_responsible"
            ):
                line.is_user_groups_only_delivery = True

    # ------------------------------------------------------
    # Onchange Method
    # ------------------------------------------------------

    @api.onchange("goods_id")
    def _onchange_goods(self):
        if self.goods_id:
            self.shipment_type_size_id = self.goods_id.shipment_type_size_id.id
            self.type_lcl = self.goods_id.type_lcl
            self.uom_id = self.goods_id.uom_id.id
            self.weight = self.goods_id.weight
            self.container_number = self.goods_id.container_number
            self.container_category_id = self.goods_id.container_category_id.id
            self.delivery_date = self.goods_id.delivery_date
            self.route_id = self.goods_id.route_id.id
            self.shipment_from = self.goods_id.route_id.shipment_from
            self.shipment_to = self.goods_id.route_id.shipment_to

    @api.onchange("vehicle_id")
    def _onchange_vehicle(self):
        if self.vehicle_id and self.vehicle_id.driver_id:
            self.driver_id = self.vehicle_id.driver_id.id

    @api.onchange("route_id")
    def _onchange_route_id(self):
        if self.route_id:
            self.shipment_from = self.route_id.shipment_from
            self.shipment_to = self.route_id.shipment_to

    # ------------------------------------------------------
    # Business Methods
    # ------------------------------------------------------

    def send_whatsapp_message(self):
        """Send whatsapp to drivers about shipping details."""
        for shipping_line in self:
            if shipping_line.driver_id and shipping_line.driver_id.mobile:
                msg = _(
                    "The goods [%s] %s will be transferred from %s to %s on %s with"
                    "  delivery date %s via vehicle %s"
                    % (
                        shipping_line.container_number,
                        shipping_line.shipment_type_size_id.name,
                        shipping_line.shipment_from,
                        shipping_line.shipment_to,
                        shipping_line.shipping_datetime,
                        shipping_line.delivery_date,
                        shipping_line.vehicle_id.name,
                    )
                )
                url = (
                    "https://api.whatsapp.com/send?phone="
                    + shipping_line.driver_id.mobile
                    + "&text="
                    + msg
                )
                return {
                    "type": "ir.actions.act_url",
                    "url": url,
                    "target": "_blank",
                }

    def send_whatsapp_message_delivery(self):
        """Send whatsapp to drivers to start delivery."""
        for shipping_line in self:
            if shipping_line.driver_id and shipping_line.driver_id.mobile:
                msg = _(
                    """Dear driver,%0a
        The goods transfer order has been issued.%0a
        Shipping details {container_number} {shipment_type} from {shipment_from} to {shipment_to} must begin.%0a
        Kindly, proceed to dispatch office
        """
                ).format(
                    container_number="[" + shipping_line.container_number + "]"
                    if shipping_line.container_number
                    else "",
                    shipment_type=str(
                        shipping_line.shipment_type_size_id.name
                        if shipping_line.shipment_type_size_id
                        else ""
                    ),
                    shipment_from=shipping_line.route_id.with_context(
                        lang=self.env.user.lang
                    ).shipment_from,
                    shipment_to=shipping_line.route_id.with_context(
                        lang=self.env.user.lang
                    ).shipment_to,
                )

                url = (
                    "https://api.whatsapp.com/send?phone="
                    + shipping_line.driver_id.mobile
                    + "&text="
                    + msg
                )
                return {
                    "type": "ir.actions.act_url",
                    "url": url,
                    "target": "_blank",
                }

    def create_reward_payment(self):
        for line in self:
            financial_settings = self.env["transportation.financial.settings"].search(
                [("company_id", "=", line.company_id.id)], limit=1
            )
            today = date.today()
            # get minimum_amount based on route dates
            (
                minimum_amount,
                parcel_transport,
                container_transport,
            ) = line.shipping_order_id.get_route_amounts(line.route_id, today)
            line.payment_reward_id = line.env["account.payment"].create(
                {
                    "shipping_order_id": line.shipping_order_id.id,
                    "clearance_request_id": line.shipping_order_id.clearance_request_id.id,
                    "journal_id": financial_settings.journal_id.id
                    if financial_settings
                    else False,
                    "partner_type": "supplier",
                    "payment_type": "outbound",
                    "amount": minimum_amount,
                    "reward": parcel_transport
                    if line.shipping_order_id.shipment_type == "lcl"
                    else container_transport,
                    "partner_id": line.driver_id.id,
                    "shipping_line_ids": [(4, line.id)],
                    "is_reward_drivers": True,
                }
            )
            line.shipping_order_id.payments_drivers_ids += line.payment_reward_id

    # ------------------------------------------------------
    # Business Methods
    # ------------------------------------------------------

    @api.depends("shipping_order_id.transport_type")
    def _compute_routes(self):
        """Calculate routes based on partner or display all."""
        for request in self:
            # if there is no clearance display all route
            request.route_ids = (
                request.shipping_order_id.clearance_request_id.statement_line_ids.mapped(
                    "route_ids"
                ).filtered(
                    lambda route: route.transport_type
                    == request.shipping_order_id.transport_type
                )
                if request.shipping_order_id.clearance_request_id
                else request.env["clearance.request.shipment.route"].search(
                    [
                        (
                            "transport_type",
                            "=",
                            request.shipping_order_id.transport_type,
                        ),
                        "|",
                        ("company_id", "=", request.shipping_order_id.company_id.id),
                        ("company_id", "=", False),
                    ]
                )
            )


class TransportationFinancialSettings(models.Model):
    _name = "transportation.financial.settings"
    _description = "Financial Settings"

    journal_id = fields.Many2one(
        "account.journal",
        domain="[('type', 'in', ['bank', 'cash'])]",
        required=1,
        string="Financial Covenant Journal",
    )
    active = fields.Boolean(default=True, string="Active")
    company_id = fields.Many2one(
        "res.company",
        "Company",
        default=lambda self: self.env.company,
        required=1,
    )
