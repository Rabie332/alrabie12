from odoo import fields, models


class RequestStage(models.Model):
    _inherit = "request.stage"

    appears_in_loan_report = fields.Boolean(string="Appears in request loan report")
