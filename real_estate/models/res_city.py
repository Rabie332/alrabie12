from odoo import fields, models


class ResCity(models.Model):
    _inherit = "res.city"
    _description = "City"

    population_density = fields.Integer("Population Density")
    land_area = fields.Integer("Land Area m²")
