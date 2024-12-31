import calendar
from datetime import date, datetime

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class UnitReservation(models.Model):
    _name = "unit.reservation"
    _description = "Property Reservation"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    def _compute_contract_count(self):
        self.contract_count = len(self.contract_id)

    @api.model
    def _get_default_team_id(self):
        return self.env["crm.team"]._get_default_team_id()

    team_id = fields.Many2one(
        "crm.team",
        string="Sales Channel",
        change_default=True,
        default=_get_default_team_id,
    )
    contract_count = fields.Integer(
        compute="_compute_contract_count", string="Contract Count", store=True
    )
    # Reservation Info
    name = fields.Char(string="Name", size=64, readonly=True)
    date = fields.Datetime(string="Date")
    date_payment = fields.Date(string="First Payment Date")
    # Building Info
    building_id = fields.Many2one("realestate.building", string="Building")
    building_code = fields.Char(string="Building Code", size=16)
    # Building Unit Info
    building_unit_id = fields.Many2one(
        "product.template",
        string="Building Unit",
        domain=[("is_property", "=", True), ("state", "=", "free")],
        required=True,
    )
    unit_code = fields.Char(string="Code", size=16)
    floor = fields.Char(string="Floor", size=16)
    price = fields.Integer(string="Price", required=True)
    template_id = fields.Many2one("installment.template", string="Payment Template")
    contract_id = fields.Many2one("realestate.contract", string="Ownership Contract")
    building_type_id = fields.Many2one("building.type", string="Building Unit Type")
    country_id = fields.Many2one("res.country", string="Country")
    city_id = fields.Many2one("res.city", string="City")
    user_id = fields.Many2one(
        "res.users", string="Responsible", default=lambda self: self.env.user
    )
    partner_id = fields.Many2one("res.partner", string="Partner")
    building_area = fields.Integer(string="Building Unit Area m²")
    reservation_line_ids = fields.One2many(
        "unit.reservation.line", "unit_reservation_id"
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirmed", "Confirmed"),
            ("contracted", "Contracted"),
            ("canceled", "Canceled"),
        ],
        string="State",
        default="draft",
    )
    type = fields.Selection(
        [("rental", "Rental"), ("ownership", "Ownership")], string="type"
    )
    company_id = fields.Many2one(
        "res.company", string="Company", default=lambda self: self.env.company
    )

    @api.onchange("building_unit_id")
    def onchange_building_unit_id(self):
        if self.building_unit_id:
            self.unit_code = self.building_unit_id.default_code
            self.floor = self.building_unit_id.floor
            self.price = self.building_unit_id.list_price
            self.building_type_id = self.building_unit_id.building_type_id
            self.building_area = self.building_unit_id.building_area
            self.company_id = self.building_unit_id.company_id.id

    @api.onchange("building_id")
    def onchange_building_id(self):
        if self.building_id:
            self.building_code = self.building_id.code
            self.country_id = self.building_id.country_id
            self.city_id = self.building_id.city_id

    def action_cancel(self):
        self.write({"state": "canceled"})
        unit = self.building_unit_id
        unit.write({"state": "free"})

    def action_confirm(self):
        self.write({"state": "confirmed"})
        unit = self.building_unit_id
        unit.write({"state": "reserved"})

    def action_contract(self):
        loan_lines = []
        if self.template_id:
            loan_lines = self._prepare_lines(self.date_payment)

        vals = {
            "type": self.type,
            "building_id": self.building_id.id,
            "country_id": self.country_id.id,
            "city_id": self.city_id.id,
            "building_code": self.building_code,
            "partner_id": self.partner_id.id,
            "unit_code": self.unit_code,
            "street": self.building_unit_id.street,
            "street2": self.building_unit_id.street2,
            "zip": self.building_unit_id.zip,
            "floor": self.floor,
            "building_unit_id": self.building_unit_id.id,
            "pricing": self.price,
            "date_payment": self.date_payment,
            "template_id": self.template_id.id if self.template_id.id else False,
            "building_type_id": self.building_type_id.id,
            "building_area": self.building_area,
            "reservation_id": self.id,
            "contract_line_ids": loan_lines,
        }

        contract_obj = self.env["realestate.contract"]
        contract_id = contract_obj.create(vals)
        self.write({"state": "contracted"})
        self.write({"contract_id": contract_id.id})

        return {
            "name": _("Ownership Contract"),
            "view_type": "form",
            "view_mode": "form",
            "res_model": "realestate.contract",
            "view_id": self.env.ref("real_estate.realestate_contract_view_form").id,
            "type": "ir.actions.act_window",
            "res_id": contract_id.id,
            "target": "current",
        }

    def view_contract(self):
        for obj in self:
            contract_id = obj.contract_id.id
            return {
                "name": _("Ownership Contract"),
                "view_mode": "form",
                "res_model": "realestate.contract",
                "view_id": self.env.ref("real_estate.realestate_contract_view_form").id,
                "type": "ir.actions.act_window",
                "res_id": contract_id,
                "target": "current",
            }

    @api.model
    def create(self, vals):
        unit_reservation = super(UnitReservation, self).create(vals)
        unit_reservation.name = self.env["ir.sequence"].next_by_code(
            "unit.reservation.seq"
        )
        return unit_reservation

    def add_months(self, sourcedate, months):
        month = sourcedate.month - 1 + months
        year = int(sourcedate.year + month / 12)
        month = month % 12 + 1
        day = min(sourcedate.day, calendar.monthrange(year, month)[1])
        return date(year, month, day)

    def _prepare_lines(self, first_date):
        loan_lines = []
        if self.template_id or self.price:
            self.reservation_line_ids = False
            price = self.price
            mon = self.template_id.duration_month
            yr = self.template_id.duration_year
            repetition = self.template_id.repetition_rate
            advance_percent = self.template_id.adv_payment_rate
            deduct = self.template_id.deduct
            if not first_date:
                raise UserError(_("Please select first payment date!"))
            first_date = datetime.strptime(str(first_date), "%Y-%m-%d").date()
            adv_payment = price * float(advance_percent) / 100
            if mon > 12:
                x = mon / 12
                mon = (x * 12) + mon % 12
            mons = mon + (yr * 12)
            if adv_payment:
                loan_lines.append(
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
                    price -= adv_payment
            if mons:
                loan_amount = (price / float(mons)) * repetition
            m = 0
            i = 2
            while m < mons:
                loan_lines.append(
                    (
                        0,
                        0,
                        {
                            "serial": i,
                            "amount": loan_amount,
                            "date": first_date,
                            "name": _("Loan Installment"),
                        },
                    )
                )
                i += 1
                first_date = self.add_months(first_date, repetition)
                m += repetition
        return loan_lines

    @api.onchange("template_id", "date_payment", "price")
    def onchange_template_id(self):
        if self.template_id:
            loan_lines = self._prepare_lines(self.date_payment)
            self.reservation_line_ids = loan_lines


class UnitReservationLine(models.Model):
    _name = "unit.reservation.line"
    _description = "Unit Reservation Line"

    date = fields.Date(string="Date")
    name = fields.Char(string="Name")
    serial = fields.Integer(string="Serial")
    amount = fields.Float(string="Payment", digits="Product Price")
    paid = fields.Boolean(string="Paid")
    unit_reservation_id = fields.Many2one(
        "unit.reservation", "", ondelete="cascade", readonly=True
    )
    partner_id = fields.Many2one(
        related="unit_reservation_id.partner_id", string="Partner"
    )
    building_id = fields.Many2one(
        related="unit_reservation_id.building_id", string="Building"
    )
    building_unit_id = fields.Many2one(
        related="unit_reservation_id.building_unit_id", string="Building Unit"
    )
