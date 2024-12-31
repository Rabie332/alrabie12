from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    clearance_request_id = fields.Many2one(
        "clearance.request", string="Clearance Request"
    )
