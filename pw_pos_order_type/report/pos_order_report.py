from odoo import fields, models


class PosOrderReport(models.Model):
    _inherit = "report.pos.order"

    order_type_id = fields.Many2one(
        "pos.order.type", string="Order Type", readonly=True
    )

    def _select(self):
        return (
            super(PosOrderReport, self)._select() + ",s.order_type_id AS order_type_id"
        )

    def _group_by(self):
        return super(PosOrderReport, self)._group_by() + ",s.order_type_id"
