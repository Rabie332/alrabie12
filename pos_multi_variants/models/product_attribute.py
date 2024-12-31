from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductAttribute(models.Model):
    _inherit = "product.attribute"

    display_type = fields.Selection(
        selection_add=[("multiple", "Multiple")], ondelete={"multiple": "cascade"}
    )

    @api.constrains("display_type")
    def _check_display_type(self):
        """check display type 'Multiple' is available for 'never' creation mode."""
        for attribute in self:
            if (
                attribute.display_type
                and attribute.display_type == "multiple"
                and attribute.create_variant != "no_variant"
            ):
                raise ValidationError(
                    _("'Multiple' display type works only with 'never' creation mode!")
                )
