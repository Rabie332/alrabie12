from odoo import fields, models


class RequestStage(models.Model):
    _inherit = "request.stage"

    appears_in_settlement_report = fields.Boolean(string="Appears in settlement report")
