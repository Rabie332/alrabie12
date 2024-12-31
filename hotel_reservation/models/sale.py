from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    price_unit = fields.Float(digits=False)

    # @api.model
    # def create(self, vals):
    #     if 'name' not in vals or not vals.get('name'):
    #         # Set a default description or implement your logic to determine the description
    #         vals['name'] = 'Default Product Description'
    #     return super(SaleOrderLine, self).create(vals)

    # def write(self, vals):
    #     if 'name' not in vals or not vals.get('name'):
    #         vals['name'] = 'Default Product Description'
    #     return super(SaleOrderLine, self).write(vals)