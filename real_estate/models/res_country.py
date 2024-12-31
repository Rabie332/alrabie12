from odoo import fields, models


class ResCountry(models.Model):
    _inherit = "res.country"

    population_density = fields.Integer(string="Population Density")
    land_area = fields.Integer(string="Land Area m²")
