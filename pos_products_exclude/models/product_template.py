from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    unavailable_pos_ids = fields.Many2many("pos.config", string="Unavailable in pos")

    def _export_for_ui(self, product):
        result = super(ProductTemplate, self)._export_for_ui(product)
        result.update(
            {
                "unavailable_pos_ids": product.unavailable_pos_ids.ids,
            }
        )
        return result
