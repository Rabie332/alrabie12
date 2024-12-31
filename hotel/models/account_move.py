# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class AccountMove(models.Model):

    _inherit = "account.move"

    reservation_id = fields.Many2one("hotel.reservation", string="Reservation")

    @api.model
    def create(self, vals):
        res = super(AccountMove, self).create(vals)
        if self._context.get("folio_id"):
            folio = self.env["hotel.folio"].browse(self._context["folio_id"])
            folio.hotel_invoice_id = res.id
            res.reservation_id = folio.reservation_id.id
        return res
