from odoo import fields, models


class BuildingType(models.Model):
    _name = "building.type"
    _description = "building type"

    name = fields.Char(string="Type", required=1)
