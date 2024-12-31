from odoo import fields, models


class DmsFolder(models.Model):
    _inherit = "dms.folder"
    _description = "Folders"

    model_ids = fields.Many2many("ir.model", string="Models")
