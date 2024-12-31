from lxml import etree

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ClearanceRequest(models.Model):
    _name = "clearance.request"
    _inherit = ["clearance.request", "rating.mixin"]
    _order = "deadline_shipment_receive asc"

    order_ids = fields.One2many(
        "shipping.order",
        "clearance_request_id",
        string="Shipping Orders",
    )
    state = fields.Selection(
        selection_add=[
            ("delivery", " Receipt and Delivery"),
            ("delivery_done", "Delivery Done"),
            ("close", "Close deal"),
        ]
    )
    shipping_order_number = fields.Integer(
        string="Shipping Orders number", compute="_compute_shipping_orders", store=1
    )
    meeting_count = fields.Integer(
        compute="_compute_meeting_count", help="Meeting Count"
    )
    requirement_ids = fields.One2many(
        "clearance.lock",
        "clearance_id",
        string="Requirements",
        readonly=True,
        states={"delivery_done": [("readonly", False)]},
    )
    display_button_close = fields.Boolean(
        compute="_compute_display_button_close", string="Display Button Close"
    )
    date_receipt = fields.Date(
        string="Date Receipt from Customer",
        readonly=True,
        states={"delivery_done": [("readonly", False)]},
    )

    shipping_order_warehouse = fields.Integer(
        string="Warehouse", compute="_compute_shipping_orders", compute_sudo=True
    )
    shipping_order_customer = fields.Integer(
        string="Customer", compute="_compute_shipping_orders", compute_sudo=True
    )
    shipping_order_port = fields.Integer(
        string="Port", compute="_compute_shipping_orders", compute_sudo=True
    )

    # ------------------------------------------------------
    # Constraints Methods
    # ------------------------------------------------------
    #
    # @api.constrains("shipping_order_number")
    # def _check_shipping_order_number(self):
    #     """Check The shipping orders number."""
    #     for clearance in self:
    #         # check the number of customer shipping orders can't be more than two
    #         if (
    #             len(
    #                 clearance.order_ids.filtered(
    #                     lambda order: order.transport_type == "customer"
    #                     and order.state != "canceled"
    #                 )
    #             )
    #             > 2
    #         ):
    #             raise ValidationError(
    #                 _("We can't create more than two customer orders")
    #             )
    #         # check the number of warehouse shipping orders can't be more than one
    #         if (
    #             len(
    #                 clearance.order_ids.filtered(
    #                     lambda order: order.transport_type == "warehouse"
    #                     and order.state != "canceled"
    #                 )
    #             )
    #             > 1
    #         ):
    #             raise ValidationError(
    #                 _("We can't create more than one warehouse orders")
    #             )
    #         # check the number of shipping orders of other can't be more than one
    #         if (
    #             len(
    #                 clearance.order_ids.filtered(
    #                     lambda order: order.transport_type == "other"
    #                     and order.state != "canceled"
    #                 )
    #             )
    #             > 1
    #         ):
    #             raise ValidationError(_("We can't create more than one other orders"))

    # ------------------------------------------------------------
    # Compute methods
    # ------------------------------------------------------------

    @api.depends("order_ids", "order_ids.transport_type", "order_ids.state")
    def _compute_shipping_orders(self):
        """Calculate orders and number of customer shipping and warehouse shipping."""
        for request in self:
            request.shipping_order_number = len(request.order_ids)
            # calculate customer shipping
            shipping_order_customer = request.order_ids.line_ids.filtered(
                lambda rec: rec.shipping_order_id.transport_type == "customer"
                and rec.shipping_order_id.state != "canceled"
            )
            # calculate warehouse shipping
            shipping_order_warehouse = request.order_ids.line_ids.filtered(
                lambda rec: rec.shipping_order_id.transport_type == "warehouse"
                and rec.shipping_order_id.state != "canceled"
            )
            # calculate empty shipping
            shipping_order_empty = len(
                request.order_ids.line_ids.filtered(
                    lambda rec: rec.shipping_order_id.transport_type == "empty"
                    and rec.shipping_order_id.state != "canceled"
                    and rec.goods_id.id
                    not in shipping_order_customer.ids + shipping_order_warehouse.ids
                )
            )
            request.shipping_order_warehouse = len(shipping_order_warehouse)
            request.shipping_order_customer = len(shipping_order_customer)
            # remove customer shipping from warehouse shipping
            for order in request.order_ids.filtered(
                lambda rec: rec.transport_type == "warehouse"
                and rec.shipping_order_id.state != "canceled"
            ):
                orders = request.env["shipping.order"].search(
                    [
                        ("shipping_order_id", "=", order.id),
                        ("transport_type", "=", "customer"),
                        ("state", "!=", "canceled"),
                    ]
                )
                request.shipping_order_warehouse -= len(orders.mapped("line_ids"))
            # calculate shipping warehouse
            if request.shipping_order_warehouse < 0 or (
                len(request.statement_line_ids)
                and len(request.statement_line_ids) == request.shipping_order_customer
            ):
                request.shipping_order_warehouse = 0
            # calculate shipping in port
            request.shipping_order_port = len(request.statement_line_ids) - (
                request.shipping_order_customer
                + request.shipping_order_warehouse
                + shipping_order_empty
            )
            if request.shipping_order_port < 0:
                request.shipping_order_port = 0

    def _compute_meeting_count(self):
        for clearance in self:
            clearance.meeting_count = (
                self.env["calendar.event"]
                .sudo()
                .search_count([("shipping_order_id", "in", self.order_ids.ids)])
            )

    @api.depends("requirement_ids", "requirement_ids.answer")
    def _compute_display_button_close(self):
        for request in self:
            request.display_button_close = False
            if (
                request.state == "delivery_done"
                and not request.requirement_ids.filtered(
                    lambda requirement: not requirement.answer
                )
            ):
                request.display_button_close = True

    # ------------------------------------------------------
    # Business Methods
    # ------------------------------------------------------

    @api.model
    def fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        """fields_view_get to no create shipping."""
        res = super(ClearanceRequest, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu
        )
        if self.env.context.get("no_display_create"):
            doc = etree.XML(res["arch"])
            for node in doc.xpath("//kanban"):
                node.set("create", "0")
            for node in doc.xpath("//tree"):
                node.set("create", "0")
            for node in doc.xpath("//form"):
                node.set("create", "0")
            res["arch"] = etree.tostring(doc, encoding="unicode")
        return res

    def shipping_order_view(self):
        """Get shipping orders for this object."""
        action = (
            self.env.ref("transportation.shipping_order_action_clearance")
            .sudo()
            .read()[0]
        )
        action["context"] = {
            "default_clearance_request_id": self.id,
            "default_company_id": self.company_id.id,
            "clearance_request_state": self.state,
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
        res = self.env["ir.actions.act_window"]._for_xml_id(
            "calendar.action_calendar_event"
        )
        res["context"] = {"default_no_create_edit": True}
        res["domain"] = [("shipping_order_id", "in", self.order_ids.ids)]
        return res

    def action_delivery(self):
        for request in self:
            # Change state
            if (
                request.request_type in ["transport", "clearance", "storage"]
                and not request.order_ids
            ):
                raise ValidationError(_("Shipping orders must be added"))
            request.state = "delivery"

    def prepare_invoice_warehousing_vals(
        self, description, product_setting, warehousing_days
    ):
        """Prepare Invoice lines"""
        accounts = False
        fiscal_position = (
            self.env["account.fiscal.position"]
            .with_company(self.company_id)
            .get_fiscal_position(self.partner_id.id, delivery_id=None)
        )
        if fiscal_position:
            accounts = (
                product_setting.clearance_product_id.product_tmpl_id.with_company(
                    self.company_id
                ).get_product_accounts(fiscal_pos=fiscal_position)
            )
        return {
            "product_id": product_setting.warehousing_product_id.id,
            "name": description,
            "quantity": warehousing_days,
            "account_id": accounts["income"].id
            if accounts
            else self.env["account.journal"]
            .search(
                [
                    ("company_id", "=", self.company_id.id),
                    ("type", "=", "sale"),
                ],
                limit=1,
            )
            .default_account_id.id,
        }

    def get_warehousing_invoice_lines(self, product_setting):
        """Get invoice warehouse lines."""
        invoice_lines = []
        # calculate free warehouse days
        free_warehousing_days = sum(
            product_setting.line_ids.filtered(
                lambda line: self.partner_id.id in line.partner_ids.ids
            ).mapped("free_warehousing_days")
        )
        for order in self.order_ids.filtered(
            lambda order: order.transport_type == "warehouse"
            and order.state != "canceled"
        ):
            # search customer shipping
            for line in (
                self.env["shipping.order"]
                .search(
                    [
                        ("shipping_order_id", "=", order.id),
                        ("transport_type", "=", "customer"),
                        ("state", "!=", "canceled"),
                    ]
                )
                .mapped("line_ids")
            ):
                # calculate warehouse days
                shipping_warehouse_line = order.line_ids.filtered(
                    lambda line_warehouse: line_warehouse.goods_id == line.goods_id
                )
                if shipping_warehouse_line:
                    warehousing_days = (
                        line.delivery_date - shipping_warehouse_line[0].delivery_date
                    ).days
                    description = "%s :  %s - %s" % (
                        line.goods_id.container_number,
                        shipping_warehouse_line[0].delivery_date,
                        line.delivery_date,
                    )
                    if warehousing_days > free_warehousing_days:
                        # prepare invoice lines
                        invoice_lines.append(
                            (
                                0,
                                0,
                                self.prepare_invoice_warehousing_vals(
                                    description,
                                    product_setting,
                                    (warehousing_days - free_warehousing_days),
                                ),
                            )
                        )
        return invoice_lines

    def action_delivery_done(self):
        # Change state
        for request in self:
            request.state = "delivery_done"
            close_deal_setting = request.env["clearance.lock.setting"].search(
                [("company_id", "=", request.company_id.id)], limit=1
            )
            if close_deal_setting:
                for requirement in close_deal_setting.requirement_ids:
                    request.sudo().requirement_ids += (
                        request.env["clearance.lock"]
                        .sudo()
                        .new({"requirement_id": requirement.id})
                    )
            # Generate customer invoice
            if not request.account_move_ids.filtered(
                lambda move: move.move_type == "out_invoice"
            ):
                if request.request_type in ["transport", "storage", "other_service"]:
                    request.create_invoice()
            # Generate warehousing invoice
            product_setting = self.env["clearance.product.invoice.setting"].search(
                [("company_id", "=", self.company_id.id)], limit=1
            )
            if product_setting.line_ids.filtered(
                lambda line: self.partner_id.id in line.partner_ids.ids
            ) and not request.account_move_ids.filtered(
                lambda move: move.move_type == "out_invoice"
                and move.is_warehouse_invoice
            ):
                invoice_lines = request.get_warehousing_invoice_lines(product_setting)
                if invoice_lines:
                    # create warehouse invoice
                    request.create_warehousing_invoice(invoice_lines)
            # send whatsapp msg to customer
            mobile = (
                request.partner_id.mobile
                if request.partner_id.mobile
                else request.partner_id.phone
            )
            if mobile:
                msg = _(
                    """Dear customer,%0awe would like to inform you that your shipment with
Farha {clearance_name} Has been delivered.
                    %0aThanks for trust.%0aFarha logistics """
                ).format(clearance_name=str(request.name))
                url = "https://api.whatsapp.com/send?phone=" + mobile + "&text=" + msg
                return {
                    "type": "ir.actions.act_url",
                    "url": url,
                    "target": "_blank",
                }

    def action_close(self):
        for request in self:
            # Check if requirement need attachment
            requirement_need_attachment = request.requirement_ids.filtered(
                lambda requirement: requirement.requirement_id.need_attachment
                and not requirement.attachment_ids
            )

            if requirement_need_attachment:
                msg = ""
                for requirement in requirement_need_attachment:
                    msg += " \n - " + requirement.requirement_id.name
                raise ValidationError(
                    _("Attachment required for requiremnts: %s") % msg
                )

            request.state = "close"
            # send mail
            users_transportation = self.env["res.users"].search(
                [
                    (
                        "groups_id",
                        "in",
                        self.env.ref(
                            "transportation.group_transportation_responsible"
                        ).id,
                    ),
                    ("email", "!=", False),
                ]
            )
            mails = users_transportation.mapped("email")
            mail = (
                self.env["mail.mail"]
                .sudo()
                .create(
                    {
                        "subject": _("Close deal Request"),
                        "body_html": _(
                            "The clearance request %s has been closed "
                            "and the shipment has been received successfully on %s"
                        )
                        % (request.name, request.date_receipt),
                        "email_to": request.partner_id.email,
                        "email_cc": ", ".join(mails),
                    }
                )
            )
            mail.sudo().send()

    def send_rating_mail_customer(self):
        for request in self:
            template = request.env.ref(
                "transportation.transportation_rating_email_template",
                raise_if_not_found=False,
            )
            if template:
                template.sudo().send_mail(request.id, force_send=True)

    def _payment_domain(self):
        """Return domain for clearance payments + not reward drivers."""
        domain = super(ClearanceRequest, self)._payment_domain() + [
            ("is_reward_drivers", "=", False)
        ]
        return domain

    def button_shipments(self, shipment_type):
        """Return packages and bales shipments"""
        clearances = self.env["clearance.request"].search([])
        shipments = clearances.mapped("statement_line_ids")
        if shipment_type == "fcl":
            return {
                "name": _("Packages"),
                "view_mode": "tree",
                "res_model": "clearance.request.shipment.type",
                "view_id": self.env.ref(
                    "clearance.clearance_request_shipment_type_package_view_tree"
                ).id,
                "type": "ir.actions.act_window",
                "domain": [("id", "in", shipments.ids), ("shipment_type", "=", "fcl")],
            }
        elif shipment_type == "lcl":
            return {
                "name": _("Parcel/Bales"),
                "view_mode": "tree",
                "res_model": "clearance.request.shipment.type",
                "view_id": self.env.ref(
                    "clearance.clearance_request_shipment_type_bale_view_tree"
                ).id,
                "type": "ir.actions.act_window",
                "domain": [("id", "in", shipments.ids), ("shipment_type", "=", "lcl")],
            }

    def action_cancel(self):
        for clearance in self:
            super(ClearanceRequest, clearance).action_cancel()
            orders = self.env["shipping.order"].search(
                [("clearance_request_id", "=", clearance.id)]
            )
            if orders:
                orders.action_cancel()


class ClearanceLock(models.Model):
    _name = "clearance.lock"
    _description = "Clearance Lock"

    requirement_id = fields.Many2one(
        "clearance.lock.requirement", string="Requirement", readonly=1
    )
    answer = fields.Boolean(string="Answer")
    attachment_ids = fields.Many2many("ir.attachment", string="Attachments")
    clearance_id = fields.Many2one("clearance.request", string="Clearance")
