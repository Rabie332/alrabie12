from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_extra = fields.Boolean(string="Is Extra")

    def _export_for_ui(self, product):
        result = super(ProductTemplate, self)._export_for_ui(product)
        result.update(
            {
                "is_extra": product.is_extra,
            }
        )
        return result
