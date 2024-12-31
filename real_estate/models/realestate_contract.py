import calendar
from datetime import date, datetime

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class RealestateContract(models.Model):
    _name = "realestate.contract"
    _description = "Real Estate Contract"

    @api.depends("contract_line_ids.amount", "contract_line_ids.paid")
    def _compute_check_amounts(self):
        total_paid = 0
        total_non_paid = 0
        total = 0
        for rec in self:
            for line in self.contract_line_ids:
                if line.paid:
                    total_paid += line.amount
                else:
                    total_non_paid += line.amount
                total += line.amount

            rec.paid = total_paid
            rec.balance = total_non_paid
            rec.total_amount = total

    paid = fields.Float(compute="_compute_check_amounts", string="Paid", store=True)
    balance = fields.Float(
        compute="_compute_check_amounts", string="Balance", store=True
    )
    total_amount = fields.Float(
        compute="_compute_check_amounts", string="Total Amount", store=True
    )

    # Real estate contract Info
    name = fields.Char("Name", size=64, readonly=True)
    reservation_id = fields.Many2one(
        "unit.reservation",
        string="Reservation",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    date = fields.Date("Date", required=True, default=fields.Date.context_today)
    date_payment = fields.Date("First Payment Date")

    # Building Info
    building_id = fields.Many2one("realestate.building", "Building")
    building_code = fields.Char(string="Building Code", size=16)

    # Building Unit Info
    building_unit_id = fields.Many2one(
        "product.template",
        string="Building Unit",
        domain=[("is_property", "=", True), ("state", "=", "free")],
        required=True,
    )
    unit_code = fields.Char(string="Unit Code", size=16)
    floor = fields.Char(string="Floor", size=16)
    street = fields.Char(string="Street")
    street2 = fields.Char(string="Street 2")
    zip = fields.Char(string="Postal code")
    origin = fields.Char(string="Source Document")
    pricing = fields.Integer(string="Price", required=True)
    template_id = fields.Many2one("installment.template", string="Payment Template")
    building_type_id = fields.Many2one("building.type", string="Building Type")
    city_id = fields.Many2one("res.city", string="City")
    user_id = fields.Many2one(
        "res.users",
        string="Responsible",
        default=lambda self: self.env.user,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    partner_id = fields.Many2one("res.partner", string="Partner", required=True)
    building_area = fields.Integer("Building Unit Area m²")
    contract_line_ids = fields.One2many(
        "realestate.contract.line", "contract_id", string="Contract Lines"
    )
    late_installments_ids = fields.One2many(
        "realestate.contract.line",
        "contract_id",
        string="Late Installments",
        compute="_compute_late_installments_ids",
    )
    country_id = fields.Many2one("res.country", string="Country")
    invoice_id = fields.Many2one("account.move", string="Invoice")
    state = fields.Selection(
        [("draft", "Draft"), ("confirmed", "Confirmed"), ("cancel", "Canceled")],
        string="State",
        default="draft",
    )
    type = fields.Selection(
        [("rental", "Rental"), ("ownership", "Ownership")],
        readonly=True,
        states={"draft": [("readonly", False)]},
        string="type",
    )
    company_id = fields.Many2one(
        "res.company", string="Company", default=lambda self: self.env.company
    )
    duration = fields.Integer(string="Contract Duration")

    @api.model
    def create(self, vals):
        realestate_contract = super(RealestateContract, self).create(vals)
        realestate_contract.name = self.env["ir.sequence"].next_by_code(
            "realestate.contract.seq"
        )
        return realestate_contract

    def action_confirm(self):
        unit = self.building_unit_id
        unit.write({"state": "sold"})
        self.write({"state": "confirmed"})

    def action_cancel(self):
        unit = self.building_unit_id
        unit.write({"state": "free"})
        self.write({"state": "cancel"})

    @api.depends("contract_line_ids", "contract_line_ids.paid")
    def _compute_late_installments_ids(self):
        """Get the late_installments"""
        for rec in self:
            rec.late_installments_ids = rec.contract_line_ids.filtered(
                lambda line: not line.paid and line.date < date.today()
            )

    @api.onchange("building_id")
    def onchange_building_id(self):
        if self.building_id:
            self.building_code = self.building_id.code
            self.country_id = self.building_id.country_id
            self.city_id = self.building_id.city_id
            unit_ids = self.env["product.template"].search(
                [("building_id", "=", self.building_id.id), ("state", "=", "free")]
            )
            building_obj = self.env["realestate.building"].browse(self.building_id.id)
            code = building_obj.code
            if building_obj:
                return {
                    "value": {"building_code": code},
                    "domain": {"building_unit_id": [("id", "in", unit_ids.ids)]},
                }

    @api.onchange("building_unit_id")
    def onchange_unit(self):
        if self.building_unit_id:
            self.unit_code = self.building_unit_id.default_code
            self.floor = self.building_unit_id.floor
            self.pricing = self.building_unit_id.list_price
            self.building_type_id = self.building_unit_id.building_type_id
            self.building_area = self.building_unit_id.building_area
            self.company_id = self.building_unit_id.company_id.id

    @api.onchange("reservation_id")
    def onchange_reservation_id(self):
        if self.reservation_id:
            self.building_id = self.reservation_id.building_id.id
            self.city_id = self.reservation_id.city_id.id
            self.building_code = self.reservation_id.building_code
            self.partner_id = self.reservation_id.partner_id.id
            self.building_unit_id = self.reservation_id.building_unit_id.id
            self.unit_code = self.reservation_id.unit_code
            self.floor = self.reservation_id.floor
            self.pricing = self.reservation_id.price
            self.date_payment = self.reservation_id.date_payment
            self.template_id = self.reservation_id.template_id.id
            self.building_type_id = self.reservation_id.building_type_id
            self.building_area = self.reservation_id.building_area
            self.company_id = self.reservation_id.company_id.id
            if self.template_id:
                contract_lines = self._prepare_lines(self.date_payment)
                self.contract_line_ids = contract_lines

    @api.onchange("template_id", "date_payment", "pricing")
    def onchange_template_id(self):
        if self.template_id or self.pricing or self.date_payment:
            contract_lines = self._prepare_lines(self.date_payment)
            self.contract_line_ids = contract_lines
            self.duration = len(contract_lines)

    def add_months(self, sourcedate, months):
        month = sourcedate.month - 1 + months
        year = int(sourcedate.year + month / 12)
        month = month % 12 + 1
        day = min(sourcedate.day, calendar.monthrange(year, month)[1])
        return date(year, month, day)

    def _prepare_lines(self, first_date):
        contract_lines = []
        self.contract_line_ids = False
        pricing = self.pricing
        mon = self.template_id.duration_month
        yr = self.template_id.duration_year
        repetition = self.template_id.repetition_rate
        advance_percent = self.template_id.adv_payment_rate
        deduct = self.template_id.deduct
        if not first_date:
            raise UserError(_("Please select first payment date!"))
        first_date = datetime.strptime(str(first_date), "%Y-%m-%d").date()
        adv_payment = pricing * float(advance_percent) / 100
        if mon > 12:
            x = mon / 12
            mon = (x * 12) + mon % 12
        mons = mon + (yr * 12)
        if adv_payment:
            contract_lines.append(
                (
                    0,
                    0,
                    {
                        "serial": 1,
                        "amount": adv_payment,
                        "date": first_date,
                        "name": _("Advance Payment"),
                    },
                )
            )
            if deduct:
                pricing -= adv_payment
        if mons:
            contract_amount = (pricing / float(mons)) * repetition
        m = 0
        i = 2
        while m < mons:
            contract_lines.append(
                (
                    0,
                    0,
                    {
                        "serial": i,
                        "amount": contract_amount,
                        "date": first_date,
                        "name": _("contract Installment"),
                    },
                )
            )
            i += 1
            first_date = self.add_months(first_date, repetition)
            m += repetition
        return contract_lines

    def create_invoice(self):
        product = self.env["product.product"].search(
            [("product_tmpl_id", "=", self.building_unit_id.id)], limit=1
        )
        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner_id.id,
                "invoice_date": self.date,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "quantity": 1,
                            "price_unit": self.pricing,
                            "product_id": product.id,
                        },
                    )
                ],
            }
        )
        if invoice:
            invoice.action_post()
            self.invoice_id = invoice.id

    def action_view_invoice(self):
        """Return view of invoice corresponding to the current contract"""
        action = self.env.ref("account.action_move_out_invoice_type").read()[0]
        action["domain"] = [("id", "=", self.invoice_id.id)]
        return action

    def set_to_draft(self):
        self.write({"state": "draft"})


class RealestateContractLine(models.Model):
    _name = "realestate.contract.line"
    _description = "Realestate Contract Line"

    contract_id = fields.Many2one(
        "realestate.contract", ondelete="cascade", string="contract", readonly=True
    )
    serial = fields.Char("#")
    date = fields.Date(string="Due Date")
    name = fields.Char(string="Name")
    amount = fields.Float(string="Payment", digits="Product Price")
    paid = fields.Boolean(string="Paid")
    company_id = fields.Many2one(
        "res.company", readonly=True, default=lambda self: self.env.user.company_id.id
    )
