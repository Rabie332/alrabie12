from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ClearanceShipmentTypeSize(models.Model):
    _name = "clearance.shipment.type.size"
    _description = "Sizes"

    name = fields.Char(string="Name")
    active = fields.Boolean(default=True, string="Active")


class ClearanceShipmentTypeLcl(models.Model):
    _name = "clearance.shipment.type.lcl"
    _description = "Shipment Types LCL"

    name = fields.Char(string="Name", translate=1)
    shipment_type_size_id = fields.Many2one(
        "clearance.shipment.type.size", string="Size"
    )
    is_unlimited = fields.Boolean(string="Unlimited")
    active = fields.Boolean(default=True, string="Active")
    shipments_number = fields.Integer()
    line_ids = fields.One2many(
        "clearance.shipment.type.lcl.line",
        "shipment_type_id",
        string="Shipments number",
    )
    is_difference_number = fields.Boolean(
        string="Calculate shipments based on numbers difference"
    )
    difference_number = fields.Integer(string="Number")
    display_button_shipments_number = fields.Boolean(
        string="Display Button Split", compute="_compute_display_shipments_number"
    )

    def create_shipments_number_type(self):
        """Fill shipments type line based on difference"""
        # get difference between number from and to
        difference = self.line_ids[-1].number_to - self.line_ids[-1].number_from
        # get shipments_number from first line
        shipments_number = self.line_ids[-1].shipments_number
        # get number_from from mast line
        number_from = self.line_ids[0].number_to + 1
        for number in range(0, self.difference_number):
            shipments_number += self.line_ids[0].shipments_number
            # create shipment type lines
            line = self.env["clearance.shipment.type.lcl.line"].new(
                {
                    "number_from": number_from,
                    "number_to": number_from + difference,
                    "shipments_number": shipments_number,
                }
            )
            number_from = line.number_to + 1
            number += 1
            self.line_ids += line

    def _compute_display_shipments_number(self):
        for shipment_type in self:
            shipment_type.display_button_shipments_number = (
                len(shipment_type.line_ids) == 1
            )

    @api.onchange("is_unlimited")
    def _onchange_is_unlimited(self):
        if self.is_unlimited:
            self.line_ids = False


class ClearanceShipmentTypeLclLine(models.Model):
    _name = "clearance.shipment.type.lcl.line"
    _description = "Shipment Types LCL Number"

    shipment_type_id = fields.Many2one(
        "clearance.shipment.type.lcl", string="Shipment Type"
    )
    number_from = fields.Integer(required=1)
    number_to = fields.Integer(required=1)
    shipments_number = fields.Integer(required=1)


class ClearanceRequestOther(models.Model):
    _name = "clearance.request.other"
    _description = "Clearance Request Other"

    name = fields.Char(string="Name", required=1)
    active = fields.Boolean("Active", default=True)


class GoodsDefinition(models.Model):
    _name = "goods.definition"
    _description = "Goods definition"

    name = fields.Char(string="Number ", required=1)
    fee_category = fields.Char(string="Fee category")
    arabic_description = fields.Text("Arabic Description", required=1)
    english_description = fields.Text("English Description", required=1)
    active = fields.Boolean("Active", default=True)


class PaymentType(models.Model):
    _name = "fees.type"
    _description = "Fees Types"

    name = fields.Char(string="Name ", required=1)
    active = fields.Boolean(default=True, string="Active")
    supplier_id = fields.Many2one(
        "res.partner",
        string="Supplier Name",
        domain="['|', ('parent_id','=', False), ('is_company','=', True)]",
    )
    is_default = fields.Boolean(string="Default")


class ContainerCategory(models.Model):
    _name = "container.category"
    _description = "Containers categories"

    name = fields.Char(string="Name ", required=1)
    is_default_value = fields.Boolean(string="Default Value")
    active = fields.Boolean(default=True, string="Active")


class ClearanceRequestInvoice(models.Model):
    _name = "clearance.request.invoice"
    _description = "Clearance Request Invoices"

    clearance_request_id = fields.Many2one(
        "clearance.request", string="Clearance Request"
    )
    invoice_type = fields.Selection(
        string="Invoice type ",
        selection=[("original", "Original"), ("copy", "Copy")],
        default="copy",
    )
    invoice_number = fields.Char(
        string="Invoice number",
    )
    supplier_name = fields.Char(
        string="Supplier Name",
    )
    delivery_method = fields.Char(
        string="Delivery method",
    )
    currency_id = fields.Many2one(
        "res.currency",
        "Currency",
        default=lambda self: self.env.ref('base.USD').id,
    )
    total = fields.Float("Total", digits=(12, 3))
    currency_code = fields.Char("Currency Code")
    country_code = fields.Char("Country of Origin")
    shipping = fields.Char("Shipping")
    number = fields.Integer("Number", readonly=1)

    @api.model
    def create(self, vals):
        """Generate number automatically unique by invoice."""
        rec = super(ClearanceRequestInvoice, self).create(vals)
        rec.number = rec._generate_sequence()
        return rec

    def _generate_sequence(self):
        invoice = self.env["clearance.request.invoice"].search(
            [
                ("id", "!=", self.id),
                ("clearance_request_id", "=", self.clearance_request_id.id),
            ],
            order="id desc",
            limit=1,
        )
        if invoice:
            number = int(invoice.number) + 1
        else:
            number = 1
        return number


class ClearanceRequestCustomsPayment(models.Model):
    _name = "clearance.request.customs.payment"
    _description = "Clearance Request Customs Payment"

    clearance_request_id = fields.Many2one(
        "clearance.request", string="Clearance Request"
    )
    payment_customs_id = fields.Many2one("account.payment", string="Payment Fees")
    fees_type_id = fields.Many2one("fees.type", string="Fees Type")
    supplier_id = fields.Many2one(
        "res.partner",
        string="Supplier Name",
        domain="['|', ('parent_id','=', False), ('is_company','=', True)]",
    )
    repayment = fields.Selection(
        string="Method Payment",
        selection=[("company", "Company"), ("customer", "Customer")],
        default="company",
    )

    def payment_fees_statement(self):
        """Get payments for this object."""

        view_id = self.env.ref("account.view_account_payment_form").id
        journal = self.env["account.journal"].search(
            [
                ("company_id", "=", self.clearance_request_id.company_id.id),
                ("type", "in", ["bank", "cash"]),
                (
                    "outbound_payment_method_ids",
                    "in",
                    [self.env.ref("clearance.account_payment_method_pay_out").id],
                ),
            ],
            limit=1,
        )
        
        if self.clearance_request_id.company_id.name in ["Farha Logistic Dammam", "فرحه لوجستك الدمام"]:
            journal = self.env["account.journal"].search(
                [
                    ("company_id", "=", self.clearance_request_id.company_id.id),
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
                    "Please define an accounting bank or cash journal"
                    ' for the company %s (%s) with payment type "pay".'
                )
                % (
                    self.clearance_request_id.company_id.name,
                    self.clearance_request_id.company_id.id,
                )
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
                "default_clearance_request_id": self.clearance_request_id.id,
                "default_partner_type": "supplier",
                "default_payment_type": "outbound",
                "default_payment_fees_customs_id": self.id,
                "default_partner_id": self.supplier_id.id,
                "default_code_supplier": self.supplier_id.code_partner,
                "default_journal_id": journal.id,
                "default_payment_method_id": self.env.ref(
                    "clearance.account_payment_method_pay_out"
                ).id,
            },
        }


class ClearanceProductInvoiceSetting(models.Model):
    _name = "clearance.product.invoice.setting"
    _description = "Clearance Product Invoice Customer"

    name = fields.Char(string="Name ", required=1)
    company_id = fields.Many2one(
        "res.company", "Company", default=lambda self: self.env.company, required=1
    )
    services_ids = fields.Many2many(
        "product.product",
        string="Other Services",
        domain="[('type', '=', 'service'),"
        "'|', ('company_id', '=', company_id), ('company_id', '=', False)]",
        required=1,
    )
    clearance_product_id = fields.Many2one(
        "product.product",
        string="Clearance Product",
        domain="[('type', '=', 'service'),"
        "'|', ('company_id', '=', company_id), ('company_id', '=', False)]",
        required=1,
    )
    transport_product_id = fields.Many2one(
        "product.product",
        string="Transport Product",
        domain="[('type', '=', 'service'),"
        "'|', ('company_id', '=', company_id), ('company_id', '=', False)]",
        required=1,
    )
    warehousing_product_id = fields.Many2one(
        "product.product",
        string="Warehousing Product",
        domain="[('type', '=', 'service'),"
        "'|', ('company_id', '=', company_id), ('company_id', '=', False)]",
        required=1,
    )
    appointment_product_id = fields.Many2one(
        "product.product",
        string="Appointment Reservation Fee Product",
        domain="[('type', '=', 'service'),"
        "'|', ('company_id', '=', company_id), ('company_id', '=', False)]",
    )
    active = fields.Boolean(default=True, string="Active")
    line_ids = fields.One2many(
        "clearance.product.invoice.setting.line",
        "setting_id",
        string="Customer Free Warehousing Days",
    )


class ClearanceProductInvoiceSettingLine(models.Model):
    _name = "clearance.product.invoice.setting.line"
    _description = "Clearance Invoice Customer Free Warehousing Days"

    setting_id = fields.Many2one("clearance.product.invoice.setting", string="Setting")
    partner_ids = fields.Many2many(
        "res.partner",
        string="Customer",
        required=True,
    )
    free_warehousing_days = fields.Integer("Free Warehousing Days")
