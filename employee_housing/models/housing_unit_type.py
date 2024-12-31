from odoo import fields, models


class HousingUnitType(models.Model):
    _name = "housing.unit.type"
    _description = "Company Building unit types"

    name = fields.Char(string='Name of Unit Type')

    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         "The unit type must be unique"),
    ]
