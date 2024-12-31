from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class RealestateBuilding(models.Model):
    _name = "realestate.building"
    _description = "Real Estate Building"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    sequence = fields.Char(string="Sequence", readonly="1")
    name = fields.Char(string="Name", size=64, required=True)

    country_id = fields.Many2one("res.country", string="Country")
    city_id = fields.Many2one("res.city", string="City")
    partner_id = fields.Many2one("res.partner", string="Owner")
    building_type_id = fields.Many2one("building.type", string="Building Type")

    price = fields.Float(string="Price")
    balcony = fields.Float(string="Balconies m²")
    building_area = fields.Float(string="Building Area m²")
    land_area = fields.Float(string="Land Area m²")
    garden = fields.Float(string="Garden m²")
    terrace = fields.Float(string="Terraces m²")
    surface = fields.Float(string="Surface")

    active = fields.Boolean(
        string="Active",
        help="If the active field is set to False, "
        "it will allow you to hide the top without removing it.",
        default=True,
    )
    handicap = fields.Boolean(string="Handicap Accessible")
    internet = fields.Boolean(string="Internet")
    alarm = fields.Boolean(string="Alarm")
    old_building = fields.Boolean(string="Old Building")
    lift = fields.Boolean(string="Lift")
    solar_electric = fields.Boolean(string="Solar Electric System")
    solar_heating = fields.Boolean(string="Solar Heating System")
    telephone = fields.Boolean(string="Telephone")
    tv_cable = fields.Boolean(string="Cable TV")
    tv_sat = fields.Boolean(string="SAT TV")
    parking_place_rentable = fields.Boolean(
        string="Parking rentable", help="Parking rentable in the location if available"
    )

    garage = fields.Integer(string="Number Garage(s)")

    description = fields.Text(string="Description")
    floor = fields.Char(string="Floor")
    code = fields.Char(string="Code")

    note = fields.Html(string="Notes")
    note_sales = fields.Text(string="Note Sales Folder")

    constructed = fields.Date(string="Construction Year")
    purchase_date = fields.Date(string="Purchase Date")
    sale_date = fields.Date(string="Sale Date")
    license_date = fields.Date(string="License Date")
    date_added = fields.Date(string="Date Added to Notarization")

    staircase = fields.Char(string="Staircase", size=8)
    street = fields.Char(string="Street")
    street2 = fields.Char(string="Street 2")
    zip = fields.Char(string="Postal code")
    license_code = fields.Char(string="License Code", size=16)
    license_location = fields.Char(string="License Notarization")
    electricity_meter = fields.Char(string="Electricity meter", size=16)
    water_meter = fields.Char(string="Water meter", size=16)
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
        string="Usage",
    )
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
            ("sold", "Sold"),
            ("blocked", "Blocked"),
        ],
        string="State",
        default="free",
    )

    company_id = fields.Many2one(
        "res.company", string="Company", default=lambda self: self.env.company
    )

    @api.model
    def create(self, vals):
        realestate = super(RealestateBuilding, self).create(vals)
        realestate.sequence = self.env["ir.sequence"].next_by_code("reservation.seq")
        return realestate

    @api.constrains("code")
    def _check_code(self):
        """Code should be unique."""
        for rec in self:
            if rec.code:
                buildings = rec.env["realestate.building"].search([])
                if buildings.filtered(
                    lambda building: building.code == rec.code and building.id != rec.id
                ):
                    raise ValidationError(_("Building code already exists !"))
