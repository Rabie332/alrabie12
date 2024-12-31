from odoo import models, fields


class HotelBranch(models.Model):
    _name = "hotel.branch"
    _description = "Hotel Branch"

    name = fields.Char("Branch Name", translate = True)