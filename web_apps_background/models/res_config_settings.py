from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    theme_background_image = fields.Binary(
        related="company_id.background_image", readonly=False, required=True
    )
