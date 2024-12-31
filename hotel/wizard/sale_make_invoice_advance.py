# See LICENSE file for full copyright and licensing details.

from odoo import models


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def create_invoices(self):
        ctx = self.env.context.copy()
        if self._context.get("active_model") == "hotel.folio":
            HotelFolio = self.env["hotel.folio"]
            folio = HotelFolio.browse(self._context.get("active_ids", []))
            folio.room_line_ids.mapped("product_id").write({"isroom": True})
            ctx.update(
                {
                    "active_ids": [folio.order_id.id],
                    "active_id": folio.order_id.id,
                    "folio_id": folio.id,
                }
            )
        res = super(SaleAdvancePaymentInv, self.with_context(ctx)).create_invoices()

        return res
