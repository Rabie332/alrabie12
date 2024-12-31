from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    insurance = fields.Boolean(string="Is Insurance")
    discount = fields.Boolean(string="Is Discount")
    returnable = fields.Boolean(string="Is Returnable")
