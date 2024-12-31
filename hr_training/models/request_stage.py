from odoo import fields, models


class RequestStage(models.Model):
    _inherit = "request.stage"

    appears_in_training_report = fields.Boolean(string="Appears in training report")
