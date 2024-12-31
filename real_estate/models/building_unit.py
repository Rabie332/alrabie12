from random import randint

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class BuildingUnit(models.Model):
    _inherit = "product.template"
    _description = "Property"

    url = fields.Char(string="Website URL")
    longitude = fields.Float(string="Longitude")
    latitude = fields.Float(string="Latitude")
    balcony = fields.Float(string="Balconies m²")
    building_area = fields.Float(string="Building Unit Area m²")
    building_area_net = fields.Float(string="Net Area m²")
    land_area = fields.Float(string="Land Area m²")
    garden = fields.Float(string="Garden m²")
    terrace = fields.Float(string="Terraces m²")
    surface = fields.Float(string="Surface")
    rental_fee = fields.Float(string="Rental fee")
    insurance_fee = fields.Float(string="Insurance fee")

    note = fields.Html(string="Notes")
    is_property = fields.Boolean(string="Property")
    alarm = fields.Boolean(string="Alarm")
    old_building = fields.Boolean(string="Old Building")
    parking_place_rentable = fields.Boolean(
        string="Parking rentable", help="Parking rentable in the location if available"
    )
    handicap = fields.Boolean(string="Handicap Accessible")
    internet = fields.Boolean(string="Internet")
    lift = fields.Boolean(string="Lift")
    phone = fields.Boolean(string="Phone")
    tv_cable = fields.Boolean(string="Cable TV")
    tv_sat = fields.Boolean(string="Sat TV")
    solar_electric = fields.Boolean(string="Solar Electric System")
    solar_heating = fields.Boolean(string="Solar Heating System")
    furniture = fields.Boolean(string="Furniture")

    building_id = fields.Many2one("realestate.building", string="Building")
    city_id = fields.Many2one("res.city", string="City")
    country_id = fields.Many2one("res.country", string="Country")
    component_ids = fields.One2many(
        "building.component.line", "unit_id", string="Components List"
    )
    partner_id = fields.Many2one("res.partner", string="Owner")
    building_type_id = fields.Many2one("building.type", string="Building Type")
    contact_ids = fields.Many2many("res.partner", string="Contacts")

    garage = fields.Integer(string="Number Garage(s)")

    heating = fields.Selection(
        [
            ("unknown", "unknown"),
            ("none", "none"),
            ("tiled_stove", "tiled stove"),
            ("stove", "stove"),
            ("central", "central heating"),
            ("self_contained_central", "self-contained central heating"),
        ],
        string="Heating",
    )
    heating_source = fields.Selection(
        [
            ("unknown", "unknown"),
            ("electricity", "Electricity"),
            ("wood", "Wood"),
            ("pellets", "Pellets"),
            ("oil", "Oil"),
            ("gas", "Gas"),
            ("district", "District Heating"),
        ],
        string="Heating Source",
    )

    purchase_date = fields.Date(string="Purchase Date")
    sale_date = fields.Date(string="Sale Date")
    license_date = fields.Date(string="License Date")
    date_added = fields.Date(string="Date Added to Notarization")

    staircase = fields.Char(string="Staircase")
    floor = fields.Char(string="Floor")
    street = fields.Char(string="Street")
    street2 = fields.Char(string="Street 2")
    zip = fields.Char(string="Postal code")
    license_code = fields.Char(string="License Code")
    license_location = fields.Char(string="License Notarization")
    electricity_meter = fields.Char(string="Electricity meter")
    water_meter = fields.Char(string="Water meter")
    north = fields.Char(string="Northen border by")
    south = fields.Char(string="Southern border by")
    east = fields.Char(string="Eastern border by")
    west = fields.Char(string="Western border by")
    usage = fields.Selection(
        [
            ("unlimited", "unlimited"),
            ("office", "Office"),
            ("shop", "Shop"),
            ("flat", "Flat"),
            ("rural", "Rural Property"),
            ("parking", "Parking"),
        ],
        "Usage",
    )
    air_condition = fields.Selection(
        [
            ("unknown", "Unknown"),
            ("none", "None"),
            ("full", "Full"),
            ("partial", "Partial"),
        ],
        string="Air Condition",
    )
    state = fields.Selection(
        [
            ("free", "Free"),
            ("reserved", "Reserved"),
            ("rented", "Rented"),
            ("sold", "Sold"),
            ("blocked", "Blocked"),
        ],
        string="State",
        default="free",
    )
    contract_ids = fields.One2many(
        "realestate.contract", "building_unit_id", string="Contracts"
    )
    analytic_account_id = fields.Many2one(
        "account.analytic.account",
        "Analytic Account",
        domain="[('company_id', '=', company_id)]",
    )
    expense_ids = fields.One2many(
        "hr.expense", "analytic_account_id", string="Expenses"
    )
    expenses_number = fields.Integer(
        string="Expenses Number", compute="_compute_expenses_number"
    )
    building_tag_ids = fields.Many2many("building.unit.tag", string="Tags")

    @api.depends("expenses_number")
    def _compute_expenses_number(self):
        for record in self:
            record.expenses_number = 0
            if record.analytic_account_id:
                record.expenses_number = (
                    record.env["hr.expense"]
                    .sudo()
                    .search_count(
                        [("analytic_account_id", "=", record.analytic_account_id.id)]
                    )
                )

    @api.onchange("building_id")
    def onchange_building_id(self):
        if self.building_id:
            self.default_code = self.building_id.code
            self.floor = self.building_id.floor
            self.list_price = self.building_id.price
            self.building_type_id = self.building_id.building_type_id
            self.building_area = self.building_id.building_area
            self.country_id = self.building_id.country_id
            self.city_id = self.building_id.city_id
            self.street = self.building_id.street
            self.street2 = self.building_id.street2
            self.zip = self.building_id.zip
            self.company_id = self.building_id.company_id.id

    @api.constrains("default_code")
    def _check_default_code(self):
        """Building code should be unique."""
        for rec in self:
            if rec.default_code:
                buildings = rec.env["product.template"].search([])
                if buildings.filtered(
                    lambda building: building.default_code == rec.default_code
                    and building.id != rec.id
                ):
                    raise ValidationError(_("Building unit code already exists !"))

    def action_expenses(self):
        return {
            "name": _("Expenses"),
            "view_type": "form",
            "view_mode": "tree,form",
            "res_model": "hr.expense",
            "view_id": False,
            "type": "ir.actions.act_window",
            "context": {"default_analytic_account_id": self.analytic_account_id.id},
            "domain": [
                ("analytic_account_id", "=", self.analytic_account_id.id),
                ("analytic_account_id", "!=", False),
            ],
        }

    def button_reserved(self):
        for unit in self:
            unit.state = "reserved"

    def button_rented(self):
        for unit in self:
            unit.state = "rented"

    def button_sold(self):
        for unit in self:
            unit.state = "sold"


class BuildingComponent(models.Model):
    _name = "building.component"
    _description = "Building Component"

    name = fields.Char(string="Name", required=True)
    furniture_details_ids = fields.One2many(
        "building.furniture", "component_id", string="Furniture List"
    )


class BuildingComponentLine(models.Model):
    _name = "building.component.line"
    _description = "Building Component Line"

    component_id = fields.Many2one(
        "building.component", string="Components", required=True
    )
    unit_id = fields.Many2one(
        "product.template", string="Building Unit", domain=[("is_property", "=", True)]
    )


class BuildingFurniture(models.Model):
    _name = "building.furniture"
    _description = "Building Furniture"

    product_id = fields.Many2one("product.product", string="Furniture", required=True)
    component_id = fields.Many2one("building.component", string="Component")


class BuildingUnitTag(models.Model):
    _name = "building.unit.tag"
    _description = "Building Unit Tag"

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char("Tag")
    color = fields.Integer(string="Color Index", default=_get_default_color)
    active = fields.Boolean("Active", default=True)
