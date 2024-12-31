# See LICENSE file for full copyright and licensing details.


from odoo import fields, models


class HotelFolio(models.Model):

    _inherit = "hotel.folio"


    folio_branch_id = fields.Many2one("hotel.branch", string="Folio Branch", related="reservation_id.reservation_branch_id", readonly=True)
    # hotel_reservation_orders_ids = fields.Many2many(
    #     "hotel.reservation.order",
    #     "hotel_res_rel",
    #     "hotel_folio_id",
    #     "reste_id",
    #     "Reservation Orders",
    # )
    # hotel_restaurant_orders_ids = fields.Many2many(
    #     "hotel.restaurant.order",
    #     "hotel_res_resv",
    #     "hfolio_id",
    #     "reserves_id",
    #     "Restaurant Orders",
    # )
