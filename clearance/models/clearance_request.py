from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ClearanceRequest(models.Model):
    _name = "clearance.request"
    _description = "Clearance Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    # ------------------------------------------------------
    # Default Method
    # ------------------------------------------------------
    @api.model
    def _default_supplier_statement(self):
        partners = self.env["res.partner"].search(
            [("zakat_tax_customs_authority", "=", True)]
        )
        if partners:
            return partners[0]

    # ------------------------------------------------------
    # Fields First State "Draft"
    # ------------------------------------------------------

    name = fields.Char(string="Request Number", readonly=1, tracking=True,)
    date = fields.Date(string="Request date", default=fields.Date.today, readonly=1, tracking=True,)
    partner_id = fields.Many2one(
        "res.partner",
        string="Customer Name",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        tracking=True,
    )
    partner_email = fields.Char(
        string="Customer Email",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        tracking=True,
    )
    partner_phone = fields.Char(
        string="Customer Phone",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        tracking=True,
    )
    request_type = fields.Selection(
        [
            ("clearance", "Clearance"),
            ("transport", "Transport"),
            ("storage", "Storage"),
            ("other_service", "Other services"),
        ],
        default="clearance",
        string="Request type",
        readonly=True,
        required=True,
        states={"draft": [("readonly", False)]},
        tracking=True,
    )
    receipt_method = fields.Selection(
        [("manual", "Manual"), ("electronic", "Electronic"), ("site", "Site")],
        string="Receipt method",
        default="manual",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        tracking=True,
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("customs_clearance", "Customs Clearance"),
            ("customs_statement", "Customs Statement"),
            ("transport", "Transport"),
            ("canceled", "canceled"),
        ],
        copy=False,
        default="draft",
        string="State",
        tracking=True,
    )
    shipping_number = fields.Char(
        string="BL Number",
        readonly=False,
        # states={"draft": [("readonly", False)]},
        tracking=True,
    )
    vessel = fields.Char(
        string="Vessel",
        readonly=True,
        translate=1,
        states={"draft": [("readonly", False)]},
        tracking=True,
    )
    port_lading = fields.Char(
        string="Port lading",
        translate=1,
        states={"draft": [("readonly", False)]},
        tracking=True,
    )
    shipping_type = fields.Selection(
        string="Shipping type",
        selection=[
            ("original", "Original"),
            ("copy", "Copy"),
            ("waybill", "Sea waybill"),
        ],
        default="original",
        readonly=True,
        states={"draft": [("readonly", False)]},
        tracking=True,
    )
    shipment_type = fields.Selection(
        [("lcl", "LCL"), ("fcl", "FCL"), ("other", "Other")],
        string="Shipment type",
        required=True,
        default="lcl",
        readonly=True,
        states={"draft": [("readonly", False)]},
        tracking=True,
    )
    shipment_type_lcl_id = fields.Many2one(
        "clearance.shipment.type.lcl",
        string="Shipment Type LCL",
        readonly=True,
        # default=_default_shipment_type_lcl,
        states={"draft": [("readonly", False)]},
        tracking=True,
    )
    number_shipment = fields.Integer(
        string="Number",
        readonly=True,
        states={"draft": [("readonly", False)]},
        tracking=True,
    )
    total_weight = fields.Float(
        string="Total Weight",
        readonly=True,
        states={"draft": [("readonly", False)]},
        tracking=True,
    )
    is_equals_weight = fields.Boolean(
        "Is Equals Weight", compute="_compute_is_equals_weight", tracking=True,
    )
    shipment_type_line_ids = fields.One2many(
        "clearance.request.shipment.type",
        "clearance_request_id",
        string="Lines",
        readonly=True,
        states={"draft": [("readonly", False)]},
        tracking=True,
    )
    clearance_invoice_ids = fields.One2many(
        "clearance.request.invoice",
        "clearance_request_id",
        string="Clearance Invoices",
        readonly=True,
        states={
            "draft": [("readonly", False)],
            "customs_clearance": [("readonly", False)],
            "customs_statement": [("readonly", False)],
        },
    )
    company_id = fields.Many2one(
        "res.company",
        "Company",
        default=lambda self: self.env.company,
        required=1,
        readonly=True,
        states={"draft": [("readonly", False)]},
        tracking=True,
    )
    account_move_ids = fields.One2many(
        "account.move", "clearance_request_id", string="Invoices"
    )
    payment_ids = fields.One2many(
        "account.payment", "clearance_request_id", string="Payments"
    )
    sale_ids = fields.One2many("sale.order", "clearance_request_id", string="Sales")
    attachment_count = fields.Integer(
        string="Attachments number",
        compute="_compute_attachment_count",
        tracking=True,
    )
    sales_number = fields.Integer(string="Sales number", compute="_compute_sales", tracking=True,)
    payments_amount = fields.Monetary(
        string="Payments Amount", compute="_compute_amount_payments", tracking=True,
    )
    invoices_amount = fields.Monetary(
        string="Invoices Amount", compute="_compute_invoices", tracking=True,
    )
    other_ids = fields.Many2many(
        "clearance.request.other",
        string="Others",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    reference = fields.Char(
        string="Reference",
        readonly=True,
        states={"draft": [("readonly", False)]},
        tracking=True,
    )
    user_id = fields.Many2one("res.users", string="Responsible", tracking=True,)
    # ------------------------------------------------------
    # Fields Second State "Customs Clearance"
    # ------------------------------------------------------

    clearance_goods_definition_ids = fields.One2many(
        "clearance.goods.definition",
        "clearance_request_id",
        string="Clearance Goods Definition",
        readonly=True,
        states={"customs_clearance": [("readonly", False)]},
    )
    shipping_agent_id = fields.Many2one(
        "res.partner",
        string="Shipping Agent Name",
        domain=[("is_shipping_agents", "=", True)],
        readonly=True,
        states={
            "draft": [("readonly", False)],
            "customs_clearance": [("readonly", False)],
            "customs_statement": [("readonly", False)],
        },
        tracking=True,
    )
    expected_date_shipment = fields.Date(
        string="Expected date of arrival shipment",
        readonly=True,
        states={
            "draft": [("readonly", False)],
            "customs_clearance": [("readonly", False)],
            "customs_statement": [("readonly", False)],
        },
        tracking=True,
    )
    last_date_empty_container = fields.Date(
        string="Last date for delivery of empty containers",
        readonly=False,
        # states={
        #     "draft": [("readonly", False)],
        #     "customs_clearance": [("readonly", False)],
        #     "customs_statement": [("readonly", False)],
        # },
        tracking=True,
    )
    repayment = fields.Selection(
        string="Repayment",
        selection=[("company", "Company"), ("customer", "Customer")],
        default="company",
        readonly=True,
        states={
            "draft": [("readonly", False)],
            "customs_clearance": [("readonly", False)],
            "customs_statement": [("readonly", False)],
        },
        tracking=True,
    )
    
    insurance = fields.Selection(
        string="Insurance",
        selection=[("yes", "Yes"), ("no", "No")],
        default="yes",
        readonly=True,
        states={
            "draft": [("readonly", False)],
            "customs_clearance": [("readonly", False)],
            "customs_statement": [("readonly", False)],
        },
        tracking=True,
    )
    payment_fees_id = fields.Many2one("account.payment", string="Payment Fees", tracking=True,)
    payment_insurance_id = fields.Many2one(
        "account.payment", string="Payment Insurance", tracking=True,
    )
    amount_insurance = fields.Monetary(
        "Amount ",
        readonly=True,
        states={
            "draft": [("readonly", False)],
            "customs_clearance": [("readonly", False)],
            "customs_statement": [("readonly", False)],
        },
        tracking=True,
    )
    currency_id = fields.Many2one(
        "res.currency",
        "Currency",
        required=True,
        default=lambda self: self.env.company.currency_id.id,
        readonly=True,
        states={
            "draft": [("readonly", False)],
            "customs_clearance": [("readonly", False)],
            "customs_statement": [("readonly", False)],
        },
        tracking=True,
    )
    delivery_authorization_number = fields.Char(
        string="Delivery Authorization Number",
        readonly=True,
        states={
            "draft": [("readonly", False)],
            "customs_clearance": [("readonly", False)],
            "customs_statement": [("readonly", False)],
        },
        tracking=True,
    )
    is_not_shipping_agent_data = fields.Boolean(
        string="Shipping Agent Data", compute="_compute_shipping_agent_data", tracking=True,
    )
    attachment_delivery_authorization_ids = fields.Many2many(
        "ir.attachment",
        "attachment_delivery_attachment_rel",
        "attachment_delivery_id",
        "attachment_id",
        string="Delivery Authorization Attachment",
        readonly=True,
        states={
            "draft": [("readonly", False)],
            "customs_clearance": [("readonly", False)],
            "customs_statement": [("readonly", False)],
        },
    )
    description = fields.Text(
        "Description",
        readonly=True,
        states={
            "draft": [("readonly", False)],
            "customs_clearance": [("readonly", False)],
            "customs_statement": [("readonly", False)],
        },
        tracking=True,
    )
    # ------------------------------------------------------
    # Fields Second State "Customs Statement"
    # ------------------------------------------------------

    clearance_document_number = fields.Char(
        string="Clearance document number",
        readonly=True,
        states={
            "draft": [("readonly", False)],
            "customs_clearance": [("readonly", False)],
            "customs_statement": [("readonly", False)],
        },
        tracking=True,
    )
    clearance_document_date = fields.Date(
        string="Clearance document date",
        readonly=True,
        states={
            "draft": [("readonly", False)],
            "customs_clearance": [("readonly", False)],
            "customs_statement": [("readonly", False)],
        },
        tracking=True,
    )
    statement_number = fields.Char(
        string="Statement number",
        readonly=True,
        states={
            "draft": [("readonly", False)],
            "customs_clearance": [("readonly", False)],
            "customs_statement": [("readonly", False)],
        },
        tracking=True,
    )
    release_statement_date = fields.Date(
        string="Release statement date",
        readonly=True,
        states={
            "draft": [("readonly", False)],
            "customs_clearance": [("readonly", False)],
            "customs_statement": [("readonly", False)],
        },
        tracking=True,
    )
    deadline_shipment_receive = fields.Date(
        string="Deadline shipment receive",
        readonly=True,
        states={
            "draft": [("readonly", False)],
            "customs_clearance": [("readonly", False)],
            "customs_statement": [("readonly", False)],
        },
        tracking=True,
    )
    is_cleared = fields.Boolean(
        string="Cleared",
        readonly=True,
        states={
            "draft": [("readonly", False)],
            "customs_clearance": [("readonly", False)],
            "customs_statement": [("readonly", False)],
        },
        tracking=True,
    )
    release_date = fields.Date(
        string="Release date",
        readonly=True,
        states={
            "draft": [("readonly", False)],
            "customs_clearance": [("readonly", False)],
            "customs_statement": [("readonly", False)],
        },
        tracking=True,
    )
    attachment_clearing_ids = fields.Many2many(
        "ir.attachment",
        "attachment_clearing_attachment_rel",
        "attachment_clearing_id",
        "attachment_id",
        string="Clearing Attachment",
        readonly=True,
        states={
            "draft": [("readonly", False)],
            "customs_clearance": [("readonly", False)],
            "customs_statement": [("readonly", False)],
        },
    )
    statement_line_ids = fields.One2many(
        "clearance.request.shipment.type",
        "clearance_request_id",
        string="Goods",
        readonly=True,
        states={
            "draft": [("readonly", False)],
            "customs_clearance": [("readonly", False)],
            "customs_statement": [("readonly", False)],
            "transport": [("readonly", False)],
        },
    )
    attachment_goods_ids = fields.Many2many(
        "ir.attachment",
        string="customs declaration Attachment",
        readonly=True,
        states={
            "draft": [("readonly", False)],
            "customs_clearance": [("readonly", False)],
            "customs_statement": [("readonly", False)],
        },
    )

    repayment_statement = fields.Selection(
        string="Repayment ",
        selection=[("company", "Company"), ("customer", "Customer")],
        default="company",
        readonly=True,
        states={
            "draft": [("readonly", False)],
            "customs_clearance": [("readonly", False)],
            "customs_statement": [("readonly", False)],
        },
        tracking=True,
    )
    supplier_statement_id = fields.Many2one(
        "res.partner",
        string="Supplier Name",
        domain="[('zakat_tax_customs_authority', '=', True)]",
        default=lambda self: self._default_supplier_statement(),
        tracking=True,
    )
    payment_fees_statement_id = fields.Many2one(
        "account.payment", string="Payment Statement Fees", tracking=True,
    )

    payment_fees_customs_ids = fields.One2many(
        "clearance.request.customs.payment",
        "clearance_request_id",
        string="Payment Customs Fees",
        readonly=True,
        states={
            "draft": [("readonly", False)],
            "customs_clearance": [("readonly", False)],
            "customs_statement": [("readonly", False)],
        },
    )
    is_not_customs_declaration_data = fields.Boolean(
        string="Customs Declaration Data", compute="_compute_customs_declaration_data", tracking=True,
    )
    is_not_goods_data = fields.Boolean(
        string="Goods Data", compute="_compute_goods_data", tracking=True,
    )
    is_not_customs_data = fields.Boolean(
        string="Customs Data", compute="_compute_customs_data", tracking=True,
    )
    service_type = fields.Selection(
        selection=[
            ("internal", "Internal"),
            ("external", "External"),
        ],
        default="internal",
        readonly=True,
        states={"draft": [("readonly", False)]},
        tracking=True,
    )

    # ------------------------------------------------------
    # Constraint Method
    # ------------------------------------------------------

    @api.constrains("shipping_number")
    def _check_shipping_number(self):
        """Check shipping_number: must be unique"""
        for clearance in self:
            if clearance.shipping_number:
                other_clearance = clearance.search(
                    [
                        ("id", "!=", clearance.id),
                        ("shipping_number", "=", clearance.shipping_number),
                    ]
                )
                if other_clearance:
                    raise ValidationError(_("BL Number must be unique"))

    # ------------------------------------------------------
    # Onchange Method
    # ------------------------------------------------------
    @api.onchange("request_type")
    def _onchange_request_type(self):
        if self.request_type in ["transport", "storage", "other_service"]:
            self.shipment_type = "other"
        else:
            self.shipment_type = "lcl"

    @api.onchange("shipment_type")
    def _onchange_shipment_type(self):
        if self.shipment_type:
            self.number_shipment = 0
            self.shipment_type_line_ids = False
            self.total_weight = 0
            self.shipment_type_lcl_id = (
                self.env["clearance.shipment.type.lcl"].search([], limit=1)
                if self.shipment_type == "lcl"
                else False
            )

    @api.onchange("partner_id")
    def _onchange_partner_id(self):
        """Get mail and phone from partner"""
        if self.partner_id:
            self.partner_email = self.partner_id.email
            self.partner_phone = self.partner_id.phone

    @api.onchange("is_cleared")
    def _onchange_cleared(self):
        if not self.is_cleared:
            self.release_date = False
            self.attachment_clearing_ids = False

    @api.onchange("last_date_empty_container")
    def _onchange_last_date_empty_container(self):
        if self.last_date_empty_container:
            self.statement_line_ids.update(
                {"last_date_empty_container": self.last_date_empty_container}
            )

    @api.onchange("deadline_shipment_receive")
    def _onchange_deadline_shipment_receive(self):
        if self.deadline_shipment_receive:
            self.statement_line_ids.update(
                {"deadline_shipment_receive": self.deadline_shipment_receive}
            )

    @api.onchange("shipment_type_lcl_id")
    def _onchange_shipment_type_lcl_id(self):
        if self.shipment_type_lcl_id:
            self.shipment_type_line_ids = False

    @api.onchange("statement_line_ids")
    def _onchange_statement_line_ids(self):
        self.number_shipment = len(self.statement_line_ids)
        # change total weight from weights of statement lines only in state transport
        if self.state == "transport":
            self.total_weight = sum(self.statement_line_ids.mapped("weight"))

    # ------------------------------------------------------
    # ORM Methods
    # ------------------------------------------------------

    @api.model
    def create(self, values):
        """Get sequence from company"""
        clearance_request = super(ClearanceRequest, self).create(values)
        if clearance_request:
            if not clearance_request.company_id.clearance_sequence_id:
                IrSequence = self.env["ir.sequence"].sudo()
                val = {
                    "name": "Sequence Clearance Request "
                    + clearance_request.company_id.name,
                    "padding": 5,
                    "code": "res.company",
                }
                clearance_request.company_id.sudo().clearance_sequence_id = (
                    IrSequence.create(val).id
                )
            clearance_request.name = (
                clearance_request.company_id.clearance_sequence_id.next_by_id()
            )
        return clearance_request

    def write(self, vals):
        res = super(ClearanceRequest, self).write(vals)
        for attachment in self.attachment_goods_ids.filtered(
            lambda attachment: not attachment.res_id
        ):
            attachment.res_id = self.id
        for attachment in self.attachment_delivery_authorization_ids.filtered(
            lambda attachment: not attachment.res_id
        ):
            attachment.res_id = self.id
        for attachment in self.attachment_clearing_ids.filtered(
            lambda attachment: not attachment.res_id
        ):
            attachment.res_id = self.id
        return res

    # ------------------------------------------------------------
    # Compute methods
    # ------------------------------------------------------------
    @api.depends("total_weight", "shipment_type_line_ids.weight", "request_type")
    def _compute_is_equals_weight(self):
        """Compute if total weight equals to sum of shipment type weight."""
        for clearance in self:
            clearance.is_equals_weight = (
                clearance.total_weight
                and sum(clearance.shipment_type_line_ids.mapped("weight"))
                != clearance.total_weight
                and clearance.request_type
                not in ["transport", "storage", "other_service"]
            )

    @api.depends("sale_ids")
    def _compute_sales(self):
        """Calculate sales."""
        for request in self:
            request.sales_number = len(request.sale_ids)

    def _payment_domain(self):
        """Return domain for clearance payments."""
        return [("clearance_request_id", "=", self.id)]

    @api.depends("payment_ids.amount_total_signed")
    def _compute_amount_payments(self):
        """Calculate payments."""
        for clearance in self:
            clearance.payments_amount = sum(
                clearance.env["account.payment"]
                .search(clearance._payment_domain())
                .mapped("amount_total_signed")
            )

    @api.depends("account_move_ids")
    def _compute_invoices(self):
        """Calculate invoices."""
        for request in self:
            request.invoices_amount = sum(
                request.account_move_ids.filtered(
                    lambda move: move.move_type == "out_invoice"
                ).mapped("amount_total_signed")
            )

    def _compute_attachment_count(self):
        """Calculate attachments number of clearance + attachments clearance payments."""
        for request in self:
            # get related clearance payments + reward payments
            payments = (
                request.env["account.payment"]
                .search([("clearance_request_id", "=", self.id)])
                .ids
            )
            request.attachment_count = request.env["ir.attachment"].search_count(
                [
                    "|",
                    "&",
                    ("res_model", "=", request._name),
                    ("res_id", "in", request.ids),
                    "&",
                    ("res_model", "=", "account.payment"),
                    ("res_id", "in", payments),
                ]
            )

    @api.depends(
        "shipping_agent_id",
        "expected_date_shipment",
        "delivery_authorization_number",
        "state",
        "payment_fees_id",
        "payment_insurance_id",
        "last_date_empty_container",
        "last_date_empty_container",
        "attachment_delivery_authorization_ids",
        "request_type",
    )
    def _compute_shipping_agent_data(self):
        for request in self:
            request.is_not_shipping_agent_data = False
            if (
                (
                    not request.shipping_agent_id
                    or not request.expected_date_shipment
                    or not request.last_date_empty_container
                    or not request.delivery_authorization_number
                    or (request.repayment == "company" and not request.payment_fees_id)
                    or (request.insurance == "yes" and not request.payment_insurance_id)
                )
                and request.state != "draft"
                and request.request_type
                not in ["transport", "storage", "other_service"]
            ):
                request.is_not_shipping_agent_data = True

    @api.depends(
        "clearance_document_number",
        "clearance_document_date",
        "statement_number",
        "release_statement_date",
        "payment_fees_statement_id",
        "deadline_shipment_receive",
        "is_cleared",
        "state",
        "attachment_clearing_ids",
        "request_type",
    )
    def _compute_customs_declaration_data(self):
        for request in self:
            request.is_not_customs_declaration_data = False
            if (
                (
                    not request.clearance_document_number
                    or not request.clearance_document_date
                    or not request.statement_number
                    or not request.release_statement_date
                    or (
                        not request.payment_fees_statement_id
                        and request.repayment_statement == "company"
                    )
                    or not request.deadline_shipment_receive
                    or (
                        request.is_cleared
                        and (
                            not request.release_date
                            or not request.attachment_clearing_ids
                        )
                    )
                )
                and request.state not in ["draft", "customs_clearance"]
                and request.request_type
                not in ["transport", "storage", "other_service"]
            ):
                request.is_not_customs_declaration_data = True

    @api.depends(
        "statement_line_ids",
        "statement_line_ids.container_number",
        "statement_line_ids.route_id",
        "statement_line_ids.delivery_date",
        "statement_line_ids.shipment_type_size_id",
        "statement_line_ids.uom_id",
        "statement_line_ids.weight",
        "state",
        "request_type",
    )
    def _compute_goods_data(self):
        for request in self:
            request.is_not_goods_data = False
            goods = request.statement_line_ids.filtered(
                lambda line: not line.container_number
            )
            if (
                request.request_type not in ["transport", "storage", "other_service"]
                and goods
                and request.state not in ["draft", "customs_clearance"]
            ):
                request.is_not_goods_data = True

    @api.depends(
        "payment_fees_customs_ids",
        "state",
        "request_type",
    )
    def _compute_customs_data(self):
        for request in self:
            request.is_not_customs_data = False
            if (
                not len(request.payment_fees_customs_ids)
                and request.state not in ["draft", "customs_clearance"]
                and request.request_type
                not in ["transport", "storage", "other_service"]
                and request.shipment_type != "lcl"
            ):
                request.is_not_customs_data = True

    # ------------------------------------------------------
    # Business Methods
    # ------------------------------------------------------
    def action_cancel(self):
        for clearance in self:
            clearance.state = "canceled"
            # cancel related invoices
            invoices = self.env["account.move"].search(
                [
                    ("clearance_request_id", "=", clearance.id),
                    ("move_type", "!=", "entry"),
                ]
            )
            if invoices:
                # cancel draft invoices
                draft_invoices = invoices.filtered(
                    lambda invoice: invoice.state == "draft"
                )
                draft_invoices.button_cancel()
                # cancel not draft invoices
                not_draft_invoices = invoices.filtered(
                    lambda invoice: invoice.state not in ["draft", "cancel"]
                )
                not_draft_invoices.button_draft()
                not_draft_invoices.button_cancel()
            # cancel related payments
            payments = self.env["account.payment"].search(clearance._payment_domain())
            if payments:
                draft_payments = payments.filtered(
                    lambda payment: payment.state == "draft"
                )
                draft_payments.action_cancel()
                not_draft_payments = payments.filtered(
                    lambda payment: payment.state not in ["draft", "cancel"]
                )
                not_draft_payments.action_draft()
                not_draft_payments.action_cancel()

    def set_to_draft(self):
        self.state = "draft"

    def _make_done_activity(self, activity_types):
        """Make done activities."""
        for clearance in self:
            activitys = self.env["mail.activity"].search(
                [
                    ("activity_type_id", "in", activity_types),
                    ("res_model", "=", clearance._name),
                    ("res_id", "=", clearance.id),
                ]
            )
            activitys.write({"active": False})

    def create_shipment_lines(self):
        """Create lines for type lcl and fcl"""
        self.shipment_type_line_ids = False
        uom_id = self.env.ref("uom.product_uom_kgm").id
        number_shipment = self.number_shipment
        # calculate number shipment based on type shipments (number shipments)
        # if shipment_type is "lcl"
        if not self.shipment_type_lcl_id.is_unlimited and self.shipment_type == "lcl":
            # get shipment by number based on type lines
            shipments_by_number = self.shipment_type_lcl_id.line_ids.filtered(
                lambda shipment_type_lcl: shipment_type_lcl.number_from
                <= number_shipment
                <= shipment_type_lcl.number_to
            )
            # calculate number shipments
            number_shipment = (
                shipments_by_number.shipments_number
                if shipments_by_number
                else self.shipment_type_lcl_id.shipments_number
            )
        # create shipment type line in clearance
        for number in range(0, number_shipment):
            vals = {"uom_id": uom_id, "quantity": 1}
            if (
                self.shipment_type == "lcl"
                and self.shipment_type_lcl_id
                != self.env.ref("clearance.clearance_shipment_type_lcl_normal")
            ):
                container_category = self.env["container.category"].search(
                    [("is_default_value", "=", True)], limit=1
                )
                # flake8: noqa: B950
                vals.update(
                    {
                        "container_number": _("Truck %s") % int(number + 1),
                        "container_category_id": container_category,
                        "shipment_type_size_id": self.shipment_type_lcl_id.shipment_type_size_id,
                    }
                )
            self.shipment_type_line_ids += self.env[
                "clearance.request.shipment.type"
            ].new(vals)

    def payment_fees_statement(self):
        """Get payments for this object."""

        view_id = self.env.ref("account.view_account_payment_form").id
        if not self.supplier_statement_id:
            raise ValidationError(_("You must filled Supplier"))
        journal = self.env["account.journal"].search(
            [
                ("company_id", "=", self.company_id.id),
                ("type", "in", ["bank", "cash"]),
                (
                    "outbound_payment_method_ids",
                    "in",
                    [self.env.ref("clearance.account_payment_method_pay_out").id],
                ),
            ],
            limit=1,
        )
        
        
        if self.company_id.name in ["Farha Logistic Dammam", "فرحه لوجستك الدمام"]:
            journal = self.env["account.journal"].search(
                [
                    ("company_id", "=", self.company_id.id),
                    ("type", "in", ["bank", "cash"]),
                    ("name", "=", "Riyad Bank"),
                    (
                        "outbound_payment_method_ids",
                        "in",
                        [self.env.ref("clearance.account_payment_method_pay_out").id],
                    ),
                ],
                limit=1,
            )
            
        if not journal:
            raise ValidationError(
                _(
                    "Please define an accounting bank or"
                    ' cash journal for the company %s (%s) with payment type "pay".'
                )
                % (self.company_id.name, self.company_id.id)
            )
        return {
            "name": _("Payments"),
            "view_mode": "form",
            "views": [(view_id, "form")],
            "res_model": "account.payment",
            "view_id": view_id,
            "type": "ir.actions.act_window",
            "res_id": False,
            "target": "current",
            "context": {
                "default_journal_id": journal.id,
                "default_payment_method_id": self.env.ref(
                    "clearance.account_payment_method_pay_out"
                ).id,
                "default_partner_id": self.supplier_statement_id.id,
                "default_code_supplier": self.supplier_statement_id.code_partner,
                "default_clearance_request_id": self.id,
                "default_partner_type": "supplier",
                "default_payment_type": "outbound",
                "default_payment_fees_statement": True,
                "default_ref": _("Customs duties"),
            },
        }

    def payment_fees(self):
        """Get payments for this object."""

        view_id = self.env.ref("account.view_account_payment_form").id
        if not self.shipping_agent_id.id:
            raise ValidationError(_("You must filled Shipping Agent"))
        journal = self.env["account.journal"].search(
            [
                ("company_id", "=", self.company_id.id),
                ("type", "in", ["bank", "cash"]),
                (
                    "outbound_payment_method_ids",
                    "in",
                    [self.env.ref("clearance.account_payment_method_pay_out").id],
                ),
            ],
            limit=1,
        )
        if self.company_id.name in ["Farha Logistic Dammam", "فرحه لوجستك الدمام"]:
            journal = self.env["account.journal"].search(
                [
                    ("company_id", "=", self.company_id.id),
                    ("type", "in", ["bank", "cash"]),
                    ("name", "=", "Riyad Bank"),
                    (
                        "outbound_payment_method_ids",
                        "in",
                        [self.env.ref("clearance.account_payment_method_pay_out").id],
                    ),
                ],
                limit=1,
            )
        if not journal:
            raise ValidationError(
                _(
                    "Please define an accounting bank "
                    'or cash journal for the company %s (%s) with payment type "pay".'
                )
                % (self.company_id.name, self.company_id.id)
            )
        return {
            "name": _("Payments"),
            "view_mode": "form",
            "views": [(view_id, "form")],
            "res_model": "account.payment",
            "view_id": view_id,
            "type": "ir.actions.act_window",
            "res_id": False,
            "target": "current",
            "context": {
                "default_clearance_request_id": self.id,
                "default_partner_id": self.shipping_agent_id.id,
                "default_code_supplier": self.shipping_agent_id.code_partner,
                "default_journal_id": journal.id,
                "default_payment_method_id": self.env.ref(
                    "clearance.account_payment_method_pay_out"
                ).id,
                "default_partner_type": "supplier",
                "default_payment_type": "outbound",
                "default_payment_fees": True,
                "default_ref": _("Shipping agent fees"),
            },
        }

    def payment_insurance(self):
        """Get payments for insurance."""

        view_id = self.env.ref("account.view_account_payment_form").id
        if not self.shipping_agent_id.id:
            raise ValidationError(_("You must filled Shipping Agent"))
        if not self.shipping_agent_id.property_account_container_deposit_id:
            raise ValidationError(
                _("You must filled Container Deposit Account of Shipping Agent")
            )
        journal = self.env["account.journal"].search(
            [
                ("company_id", "=", self.company_id.id),
                ("type", "in", ["bank", "cash"]),
                (
                    "outbound_payment_method_ids",
                    "in",
                    [self.env.ref("clearance.account_payment_method_pay_out").id],
                ),
            ],
            limit=1,
        )
        if self.company_id.name in ["Farha Logistic Dammam", "فرحه لوجستك الدمام"]:
            journal = self.env["account.journal"].search(
                [
                    ("company_id", "=", self.company_id.id),
                    ("type", "in", ["bank", "cash"]),
                    ("name", "=", "Riyad Bank"),
                    (
                        "outbound_payment_method_ids",
                        "in",
                        [self.env.ref("clearance.account_payment_method_pay_out").id],
                    ),
                ],
                limit=1,
            )
        if not journal:
            raise ValidationError(
                _(
                    "Please define an accounting bank "
                    'or cash journal for the company %s (%s) with payment type "pay".'
                )
                % (self.company_id.name, self.company_id.id)
            )
        # flake8: noqa: B950
        return {
            "name": _("Payments"),
            "view_mode": "form",
            "views": [(view_id, "form")],
            "res_model": "account.payment",
            "view_id": view_id,
            "type": "ir.actions.act_window",
            "res_id": False,
            "target": "current",
            "context": {
                "default_clearance_request_id": self.id,
                "default_partner_id": self.shipping_agent_id.id,
                "default_code_supplier": self.shipping_agent_id.code_partner,
                "default_journal_id": journal.id,
                "default_payment_method_id": self.env.ref(
                    "clearance.account_payment_method_pay_out"
                ).id,
                "default_partner_type": "supplier",
                "default_payment_type": "outbound",
                "default_destination_account_id": self.shipping_agent_id.property_account_container_deposit_id.id,
                "default_amount": self.amount_insurance,
                "default_ref": _("Insurance"),
                "default_payment_insurance": True,
            },
        }

    def attachment_tree_view(self):
        """Get attachments for clearance and clearance payments ."""
        # Get payment for clearance + drivers rewards
        payments = (
            self.env["account.payment"]
            .search([("clearance_request_id", "=", self.id)])
            .ids
        )

        attachment_action = self.env.ref("base.action_attachment")
        action = attachment_action.sudo().read()[0]
        action["context"] = {
            "default_res_model": "clearance.request",
            "default_res_id": self.ids[0],
            "clearance_request_state": self.state,
        }

        action["domain"] = str(
            [
                "|",
                "&",
                ("res_model", "=", self._name),
                ("res_id", "in", self.ids),
                "&",
                ("res_model", "=", "account.payment"),
                ("res_id", "in", payments),
            ]
        )
        return action

    def action_view_invoices(self):
        """Return view of invoice corresponding to the current contract"""
        action = self.env.ref("account.action_move_out_invoice_type").sudo().read()[0]
        action["domain"] = [
            ("clearance_request_id", "=", self.id),
            ("move_type", "!=", "entry"),
        ]
        action["context"] = {
            "default_clearance_request_id": self.id,
            "default_ref": self.name,
            "default_invoice_origin": self.name,
            "clearance_request_state": self.state,
            "default_move_type": "out_invoice",
            "default_partner_id": self.partner_id.id,
        }
        return action

    def sales_tree_view(self):
        """Get sales for this object."""
        action = self.env.ref("sale.action_orders").sudo().read()[0]
        action["domain"] = [("clearance_request_id", "=", self.id)]
        action["context"] = {
            "default_clearance_request_id": self.id,
            "clearance_request_state": self.state,
            "default_partner_id": self.partner_id.id,
        }
        return action

    def payments_tree_view(self):
        """Get payments for this object."""
        action = self.env.ref("account.action_account_payments").sudo().read()[0]
        action["domain"] = self._payment_domain()
        action["context"] = {
            "default_clearance_request_id": self.id,
            "clearance_request_state": self.state,
            "default_partner_type": "customer",
        }
        return action

    def action_send(self):
        for request in self:
            if request.request_type in ["transport", "storage", "other_service"]:
                request.state = "transport"
            else:
                if not request.shipping_number or not request.vessel:
                    raise ValidationError(_("You must filled Shipping Policy Data"))
                if request.attachment_count < 2:
                    raise ValidationError(
                        _(
                            "Please make sure to attach the following files: "
                            "\n - A picture of the policy "
                            "\n - A picture of the commercial invoice"
                        )
                    )
                for translation_officer in self.env["res.users"].search(
                    [
                        (
                            "groups_id",
                            "in",
                            self.env.ref("clearance.group_translation_officer").id,
                        ),
                        ("company_ids", "in", [request.company_id.id]),
                    ]
                ):
                    request.activity_schedule(
                        "clearance.mail_translation_officer_approval",
                        user_id=translation_officer.id,
                    )
                for shipping_agent_responsible in self.env["res.users"].search(
                    [
                        (
                            "groups_id",
                            "in",
                            self.env.ref(
                                "clearance.group_shipping_agent_responsible"
                            ).id,
                        ),
                        ("company_ids", "in", [request.company_id.id]),
                    ]
                ):
                    request.activity_schedule(
                        "clearance.mail_shipping_agent_responsible_approval",
                        user_id=shipping_agent_responsible.id,
                    )
                request.state = "customs_clearance"

    def action_customs_statement(self):
        for request in self:
            fees_type_ids = self.env["fees.type"].search([("is_default", "=", True)])
            for fees_type_id in fees_type_ids:
                self.payment_fees_customs_ids += self.env[
                    "clearance.request.customs.payment"
                ].new(
                    {
                        "clearance_request_id": self.id,
                        "fees_type_id": fees_type_id.id,
                        "supplier_id": fees_type_id.supplier_id.id or False,
                    }
                )
            if not len(
                request.clearance_goods_definition_ids
            ) or request.clearance_goods_definition_ids.filtered(
                lambda clearance_goods: not clearance_goods.goods_definition_id
                or not clearance_goods.goods_description
            ):
                raise ValidationError(_("You must filled Translation Data"))
            # make done all old activities
            request._make_done_activity(
                [
                    request.env.ref("clearance.mail_translation_officer_approval").id,
                    request.env.ref(
                        "clearance.mail_shipping_agent_responsible_approval"
                    ).id,
                ]
            )
            request.state = "customs_statement"

    def _prepare_invoice_values(self, customer, fiscal_position, payment_term):
        """Prepare invoice Values from clearance related payments.."""
        vals_invoice_lines = []
        if not self.env["clearance.product.invoice.setting"].search(
            [("company_id", "=", self.company_id.id)], limit=1
        ):
            raise ValidationError(
                _(
                    "Clearance and transportation "
                    "services products must be selected in Settings"
                )
            )
        supplier_payments = self.payment_ids.filtered(
            lambda payment: payment.partner_type == "supplier"
            and payment.state != "cancel"
            and payment != self.payment_insurance_id
            and not payment.is_reward_drivers
        )
        for payment in supplier_payments:
            vals_invoice_lines.append(
                (
                    0,
                    0,
                    {
                        "name": payment.ref,
                        "price_unit": payment.amount,
                    },
                )
            )

        invoice_vals = {
            "ref": self.name,
            "invoice_origin": self.name,
            "move_type": "out_invoice",
            "invoice_date": fields.Date.today(),
            "company_id": self.company_id.id,
            "journal_id": self.env["account.journal"]
            .search(
                [("company_id", "=", self.company_id.id), ("type", "=", "sale")],
                limit=1,
            )
            .id,
            "partner_id": customer,
            "fiscal_position_id": fiscal_position,
            "currency_id": self.company_id.currency_id.id,
            "invoice_payment_term_id": payment_term,
            "clearance_request_id": self.id,
            "invoice_line_ids": vals_invoice_lines,
        }
        return invoice_vals

    def action_transport(self):
        for request in self:
            if (
                request.is_not_shipping_agent_data
                or request.is_not_customs_declaration_data
                or request.is_not_goods_data
                or request.is_not_customs_data
            ):
                raise ValidationError(_("You must filled all Clearance Request Data"))
            payment_ids = request.env["account.payment"].search(
                request._payment_domain()
            )
            if payment_ids.filtered(
                lambda payment: payment.state not in ("posted", "cancel")
            ):
                raise ValidationError(_("All payments must be posted"))
            if not request.account_move_ids.filtered(
                lambda move: move.move_type == "out_invoice"
            ):
                if request.request_type == "clearance":
                    request.create_clearance_invoice()
            # Change state
            request.state = "transport"

    def create_empty_invoice(self):
        fiscal_position = (
            self.env["account.fiscal.position"]
            .with_company(self.company_id)
            .get_fiscal_position(self.partner_id.id, delivery_id=None)
        )
        payment_term = self.partner_id.property_payment_term_id
        invoice_vals = self._prepare_invoice_values(
            self.partner_id.id, fiscal_position, payment_term
        )
        invoice = self.env["account.move"].create(invoice_vals)
        invoice._onchange_partner_id_account_invoice_pricelist()
        return invoice

    def create_invoice(self):
        invoice = self.create_empty_invoice()
        for line in self.statement_line_ids:
            line_vals = {
                "move_id": invoice.id,
                "account_id": invoice.journal_id.default_account_id.id,
            }
            if self.request_type in ["transport", "storage"]:
                line_vals.update(
                    {
                        "name": line.route_id.name,
                        "product_id": line.route_id.product_id.id,
                        "quantity": 1,
                    }
                )
                invoice_line = (
                    self.env["account.move.line"]
                    .with_context(check_move_validity=False)
                    .create(line_vals)
                )
            else:
                line_vals.update(
                    {
                        "name": line.service_id.name,
                        "product_id": line.service_id.id,
                        "quantity": line.quantity,
                    }
                )
                invoice_line = (
                    self.env["account.move.line"]
                    .with_context(check_move_validity=False)
                    .create(line_vals)
                )
        #  Add a line to the invoice with all products associated with the partner.
        for product in self.partner_id.product_ids:
            line_vals = {
                "move_id": invoice.id,
                "account_id": invoice.journal_id.default_account_id.id,
                "name": product.name,
                "product_id": product.id,
                "quantity": 1,
            }
            invoice_line += (
                self.env["account.move.line"]
                .with_context(check_move_validity=False)
                .create(line_vals)
            )
        if invoice_line:
            invoice_line._onchange_product_id()
            invoice_line._onchange_product_id_account_invoice_pricelist()
            invoice_line._onchange_uom_id()
        invoice.with_context(check_move_validity=False)._onchange_invoice_line_ids()
        invoice.with_context(check_move_validity=False)._recompute_tax_lines()

    def create_clearance_invoice_line(self, invoice, product, account):
        """Ccreate invoice line for clearance, transport and appointment"""
        # create invoice line
        invoice_line = (
            self.env["account.move.line"]
            .with_context(check_move_validity=False)
            .create(
                {
                    "product_id": product,
                    "quantity": len(self.statement_line_ids),
                    "move_id": invoice,
                    "account_id": account,
                }
            )
        )
        invoice_line._onchange_product_id()
        invoice_line._onchange_product_id_account_invoice_pricelist()
        invoice_line._onchange_uom_id()
        return invoice_line

    def create_clearance_invoice(self):
        # Generate customer invoice
        invoice = self.create_empty_invoice()
        fiscal_position = invoice.fiscal_position_id
        product_setting = self.env["clearance.product.invoice.setting"].search(
            [("company_id", "=", self.company_id.id)], limit=1
        )
        accounts = False
        if fiscal_position:
            accounts = (
                product_setting.clearance_product_id.product_tmpl_id.with_company(
                    self.company_id
                ).get_product_accounts(fiscal_pos=fiscal_position)
            )
        # create clearance invoice line
        self.create_clearance_invoice_line(
            invoice.id,
            product_setting.clearance_product_id.id,
            accounts["income"].id
            if accounts
            else invoice.journal_id.default_account_id.id,
        )
        # create transport invoice line
        self.create_clearance_invoice_line(
            invoice.id,
            product_setting.transport_product_id.id,
            accounts["income"].id
            if accounts
            else invoice.journal_id.default_account_id.id,
        )
        # create appointment invoice line
        if self.request_type == "clearance":
            # create invoice line with unit price and taxes if
            # clearance type is clearance and shipment fcl
            invoice_appointment_line = self.create_clearance_invoice_line(
                invoice.id,
                product_setting.appointment_product_id.id,
                accounts["income"].id
                if accounts
                else invoice.journal_id.default_account_id.id,
            )
            # remove unit price and taxes if clearance type is
            # clearance and shipment lcl  ( should be enter manually)
            if self.shipment_type in ["lcl", "other"]:
                invoice_appointment_line.price_unit = 0
                invoice_appointment_line.tax_ids = False
        for product in self.partner_id.product_ids:
            line_vals = {
                "move_id": invoice.id,
                "account_id": invoice.journal_id.default_account_id.id,
                "name": product.name,
                "product_id": product.id,
                "quantity": 1,
            }
            invoice_line = (
                self.env["account.move.line"]
                .with_context(check_move_validity=False)
                .create(line_vals)
            )
            invoice_line._onchange_product_id()
            invoice_line._onchange_product_id_account_invoice_pricelist()
            invoice_line._onchange_uom_id()
        invoice.with_context(check_move_validity=False)._onchange_invoice_line_ids()
        invoice.with_context(check_move_validity=False)._recompute_tax_lines()

    def create_warehousing_invoice(self, invoice_lines):
        # Generate warehousing invoice
        if invoice_lines:
            fiscal_position = (
                self.env["account.fiscal.position"]
                .with_company(self.company_id)
                .get_fiscal_position(self.partner_id.id, delivery_id=None)
            )
            # Create Invoice
            invoice = (
                self.env["account.move"]
                .with_context(check_move_validity=False)
                .create(
                    {
                        "ref": self.name,
                        "invoice_origin": self.name,
                        "move_type": "out_invoice",
                        "invoice_date": fields.Date.today(),
                        "company_id": self.company_id.id,
                        "journal_id": self.env["account.journal"]
                        .search(
                            [
                                ("company_id", "=", self.company_id.id),
                                ("type", "=", "sale"),
                            ],
                            limit=1,
                        )
                        .id,
                        "partner_id": self.partner_id.id,
                        "fiscal_position_id": fiscal_position,
                        "currency_id": self.company_id.currency_id.id,
                        "invoice_payment_term_id": self.partner_id.property_payment_term_id,
                        "clearance_request_id": self.id,
                        "is_warehouse_invoice": True,
                        "invoice_line_ids": invoice_lines,
                    }
                )
            )
            # update invoice lines
            for invoice_line in invoice.invoice_line_ids:
                description = invoice_line.name
                invoice_line._onchange_product_id()
                invoice_line._onchange_product_id_account_invoice_pricelist()
                invoice_line._onchange_uom_id()
                # Change description
                invoice_line.name = description
            invoice.with_context(check_move_validity=False)._onchange_invoice_line_ids()
            invoice.with_context(check_move_validity=False)._recompute_tax_lines()

    @api.model
    def send_mail_deadline_shipment_receive(self):
        today = fields.Date.from_string(fields.Date.today())
        clearances = self.sudo().search([("deadline_shipment_receive", "!=", False)])
        users = self.env["res.users"].search(
            [
                (
                    "groups_id",
                    "in",
                    self.env.ref("clearance.group_customs_declaration_responsible").id,
                )
            ]
        )
        for clearance in clearances:
            if (
                clearance.deadline_shipment_receive
                and (clearance.deadline_shipment_receive - relativedelta(days=3))
                == today
            ):
                # send mail to users
                for user in users:
                    mail = (
                        self.env["mail.mail"]
                        .sudo()
                        .create(
                            {
                                "subject": _("Last date to receive the shipment"),
                                "body_html": _(
                                    "The last date for receiving the shipment is"
                                    " %s for the clearance request %s"
                                )
                                % (clearance.deadline_shipment_receive, clearance.name),
                                "email_to": user.email,
                            }
                        )
                    )
                    mail.sudo().send()


class ClearanceRequestShipmentType(models.Model):
    _name = "clearance.request.shipment.type"
    _description = "Clearance Request Shipment Type"
    _rec_name = "container_number"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _log_access = True

    def name_get(self):
        res = []
        for shipment in self:
            res.append(
                (
                    shipment.id,
                    "[{}] {} ".format(
                        shipment.container_number
                        or shipment.truck_type_id
                        and shipment.truck_type_id.name
                        or "",
                        shipment.shipment_type_size_id.name or "",
                    ),
                )
            )
        return res

    clearance_request_id = fields.Many2one(
        "clearance.request", string="Clearance Request", tracking=True,
    )
    statement_number = fields.Char(
        string="Statement Number",
        related="clearance_request_id.statement_number",
        store=1,
        tracking=True,
    )
    partner_id = fields.Many2one(
        string="Customer Name", related="clearance_request_id.partner_id", store=1,tracking=True,
    )
    shipping_number = fields.Char(
        string="BL Number",
        related="clearance_request_id.shipping_number",
        store=1,
        tracking=True,
    )
    shipment_type_size_id = fields.Many2one(
        "clearance.shipment.type.size", string="Size", tracking=True,
    )
    type_lcl = fields.Selection(
        string="Type",
        selection=[("bale", "Bale"), ("package", "Package")],
        default="bale",
        tracking=True,
    )
    uom_id = fields.Many2one("uom.uom", "Unit of Measure", tracking=True,)
    weight = fields.Float(string="Weight", tracking=True,)
    container_number = fields.Char(string="Container Number", tracking=True,)
    route_id = fields.Many2one("clearance.request.shipment.route", string="Route", tracking=True,)
    shipment_from = fields.Char(string="From", tracking=True,)
    shipment_to = fields.Char(string="To", tracking=True,)
    delivery_date = fields.Date(string="Delivery date", tracking=True,)
    company_id = fields.Many2one(
        "res.company", "Company", related="clearance_request_id.company_id", store=1, tracking=True,
    )
    container_category_id = fields.Many2one(
        "container.category", string="Container Category", tracking=True,
    )
    customer_location = fields.Char(string="Customer location", tracking=True,)
    deadline_shipment_receive = fields.Date(string="Deadline shipment receive", tracking=True,)
    last_date_empty_container = fields.Date(
        string="Last date for delivery of empty containers",
        tracking=True,
    )
    shipment_type = fields.Selection(
        string="Shipment type", related="clearance_request_id.shipment_type", store=1, tracking=True,
    )
    state = fields.Selection(
        related="clearance_request_id.state", string="State", store=True, tracking=True,
    )
    truck_type_id = fields.Many2one("container.category", "Truck Type", tracking=True,)
    service_id = fields.Many2one(
        "product.product", domain=[("type", "=", "service")], string="Service", tracking=True,
    )
    quantity = fields.Float("Quantity", tracking=True,)
    route_ids = fields.Many2many(
        "clearance.request.shipment.route", string="Routes", compute="_compute_routes", 
    )

    @api.onchange("route_id")
    def _onchange_route_id(self):
        if self.route_id:
            self.shipment_from = self.route_id.shipment_from
            self.shipment_to = self.route_id.shipment_to

    @api.depends("clearance_request_id.partner_id")
    def _compute_routes(self):
        """Calculate routes based on partner."""
        for request in self:
            request.route_ids = request.clearance_request_id.partner_id.mapped(
                "clearance_route_ids.route_id"
            )


class ClearanceRequestShipmentRoute(models.Model):
    _name = "clearance.request.shipment.route"
    _description = "Clearance Request Shipment Route"

    name = fields.Char(string="Name", readonly=0)
    shipment_from = fields.Char(string="From", required=1, translate=1)
    shipment_to = fields.Char(string="To", required=1, translate=1)
    currency_id = fields.Many2one(
        "res.currency",
        "Currency",
        required=True,
        default=lambda self: self.env.company.currency_id.id,
    )
    container_transport = fields.Monetary("Container transport")
    parcel_transport = fields.Monetary("Parcel transport ")
    minimum_amount = fields.Monetary("Minimum Amount")
    active = fields.Boolean(default=True, string="Active")
    company_id = fields.Many2one(
        "res.company",
        "Company",
        default=lambda self: self.env.company,
    )
    product_id = fields.Many2one("product.product", string="Product")
    transport_type = fields.Selection(
        string="Transport type",
        selection=[
            ("warehouse", "Yard"),
            ("customer", "Customer site"),
            ("other", "Other site"),
            ("empty", "Return empty"),
        ],
    )
    line_ids = fields.One2many(
        "clearance.request.shipment.route.line",
        "route_id",
        string="Route Amounts",
    )
    line_price_ids = fields.One2many(
        "clearance.request.shipment.route.price",
        "route_id",
        string="Route Prices",
    )

    @api.model
    def create(self, values):
        route = super(ClearanceRequestShipmentRoute, self).create(values)
        if route:
            route.name = str(route.shipment_from) + "-" + str(route.shipment_to)
        return route

    def write(self, vals):
        route = super(ClearanceRequestShipmentRoute, self).write(vals)
        if vals.get("shipment_from", False) or vals.get("shipment_to", False):
            self.name = str(self.shipment_from) + "-" + str(self.shipment_to)
        return route


class ClearanceRequestShipmentRouteLine(models.Model):
    _name = "clearance.request.shipment.route.line"
    _description = "Clearance Request Shipment Route Amount"

    route_id = fields.Many2one("clearance.request.shipment.route", string="Route")
    date_from = fields.Date(string="Date from", required=1)
    date_to = fields.Date(string="Date to", required=1)
    container_transport = fields.Monetary("Container transport")
    parcel_transport = fields.Monetary("Parcel transport ")
    minimum_amount = fields.Monetary("Minimum Amount")
    currency_id = fields.Many2one(
        "res.currency",
        "Currency",
        required=True,
    )


class ClearanceRequestShipmentRoutePrice(models.Model):
    _name = "clearance.request.shipment.route.price"
    _description = "Clearance Request Shipment Route Price"

    route_id = fields.Many2one("clearance.request.shipment.route", string="Route")
    date_from = fields.Date(string="Date from", required=1)
    date_to = fields.Date(string="Date to", required=1)
    amount = fields.Monetary("Amount")
    currency_id = fields.Many2one(
        "res.currency",
        "Currency",
        required=True,
    )


class ClearanceGoodsDefinition(models.Model):
    _name = "clearance.goods.definition"
    _description = "Clearance Goods definition"

    goods_definition_id = fields.Many2one(
        "goods.definition", string="Tariff Item", required=1
    )
    goods_description = fields.Text("Goods Description", required=1)
    fee_category = fields.Char(string="Fee category")
    standing_weight = fields.Float(string="Standing Weight", digits=(12, 3))
    net_weight = fields.Float(string="Net Weight", digits=(12, 3))
    quantity = fields.Float(string="Quantity", digits=(12, 3))
    unity_code = fields.Char(string="Unity Code")
    user = fields.Char("Unity Create User")
    clearance_request_id = fields.Many2one("clearance.request", string="Clearance")
    paragraph = fields.Text("Paragraph")
    exemption_number = fields.Char("Exemption Number")
    value_foreign_currency = fields.Float("Value In Foreign Currency", digits=(12, 3))
    insurance = fields.Char("Insurance")

    @api.onchange("goods_definition_id")
    def _onchange_goods_definition(self):
        """Change Goods definition."""
        if self.goods_definition_id:
            self.goods_description = self.goods_definition_id.arabic_description
            self.fee_category = self.goods_definition_id.fee_category
