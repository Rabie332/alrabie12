
# See LICENSE file for full copyright and licensing details.
# invoice_ids
from odoo import api, fields, models


class HotelFolio(models.Model):

    _inherit = "hotel.folio"
    _order = "reservation_id desc"

    reservation_id = fields.Many2one(
        "hotel.reservation", "Reservation", ondelete="restrict"
    )
    duration = fields.Integer(related="reservation_id.duration", store=1)
    reservation_type = fields.Selection(
        related="reservation_id.reservation_type", store=1
    )
    room_rate = fields.Float(related="reservation_id.room_rate", store=1)
    total_room_rate = fields.Float(related="reservation_id.total_room_rate", store=1)
    discount = fields.Float(related="reservation_id.discount", store=1)
    insurance = fields.Float(related="reservation_id.insurance", store=1)
    taxes_amount = fields.Float(related="reservation_id.taxes_amount", store=1)
    taxed_total_rate = fields.Float(related="reservation_id.taxed_total_rate", store=1)
    total_cost = fields.Float(related="reservation_id.total_cost", store=1)
    final_cost = fields.Float(related="reservation_id.final_cost", store=1)
    rent = fields.Selection(related="reservation_id.rent", store=1)
    payments_count = fields.Float(related="reservation_id.payments_count", store=1)
    balance = fields.Float(related="reservation_id.balance", store=1)
    service_amount = fields.Float(
        string="Services", compute="_compute_service_amount", store=1
    )
    service_tax = fields.Float(
        string="Services Tax", compute="_compute_service_amount", store=1
    )
    is_returnable = fields.Boolean(related="reservation_id.is_returnable", store=1)
    returnable_amount = fields.Float(
        related="reservation_id.returnable_amount", store=1
    )

    def write(self, vals):
        res = super(HotelFolio, self).write(vals)
        reservation_line_obj = self.env["hotel.room.reservation.line"]
        for folio in self:
            reservations = reservation_line_obj.search(
                [("reservation_id", "=", folio.reservation_id.id)]
            )
            if len(reservations) == 1:
                # Create reservation line in room
                for room in folio.reservation_id.reservation_line.mapped("room_id"):
                    vals = {
                        "room_id": room.id,
                        "check_in": folio.checkin_date,
                        "check_out": folio.checkout_date,
                        "state": "assigned",
                        "reservation_id": folio.reservation_id.id,
                    }
                    reservations.write(vals)
        return res

    def _update_folio_line(self, folio_id):
        """Update folio lines"""
        folio_room_line_obj = self.env["folio.room.line"]
        hotel_room_obj = self.env["hotel.room"]
        for rec in folio_id:
            for room_rec in rec.room_line_ids:
                room = hotel_room_obj.search(
                    [("product_id", "=", room_rec.product_id.id)], limit=1
                )
                room.write({"isroom": False})
                # Create folio romm line with reservation line
                vals = {
                    "room_id": room.id,
                    "check_in": rec.checkin_date,
                    "check_out": rec.checkout_date,
                    "folio_id": rec.id,
                    "reservation_line_id": room_rec.reservation_line_id.id,
                }
                folio_room_line_obj.create(vals)

    @api.depends("service_line_ids", "service_line_ids.price_subtotal")
    def _compute_service_amount(self):
        """Calculate service amount and service taxes"""
        for folio in self:
            taxes_amount = 0
            for service_line in folio.service_line_ids:
                taxes = service_line.tax_id.compute_all(
                    service_line.price_unit,
                    service_line.currency_id,
                    service_line.product_uom_qty,
                    product=service_line.product_id,
                )
                taxes_amount += sum(
                    tax.get("amount", 0.0) for tax in taxes.get("taxes", [])
                )
            folio.service_amount = sum(folio.service_line_ids.mapped("price_subtotal"))
            folio.service_tax = taxes_amount


class HotelFolioLine(models.Model):

    _inherit = "hotel.folio.line"

    reservation_line_id = fields.Many2one("hotel.reservation.line", "Reservation Line")

    @api.onchange("checkin_date", "checkout_date")
    def _onchange_checkin_checkout_dates(self):
        res = super(HotelFolioLine, self)._onchange_checkin_checkout_dates()
        avail_prod_ids = []
        for room in self.env["hotel.room"].search([]):
            assigned = False
            for line in room.room_reservation_line_ids.filtered(
                lambda l: l.status != "cancel"
            ):
                if self.checkin_date and line.check_in and self.checkout_date:
                    if (self.checkin_date <= line.check_in <= self.checkout_date) or (
                        self.checkin_date <= line.check_out <= self.checkout_date
                    ):
                        assigned = True
                    elif (line.check_in <= self.checkin_date <= line.check_out) or (
                        line.check_in <= self.checkout_date <= line.check_out
                    ):
                        assigned = True
            if not assigned:
                avail_prod_ids.append(room.product_id.id)
        return res

    def write(self, vals):
        """
        Overrides orm write method.
        @param self: The object pointer
        @param vals: dictionary of fields value.
        Update Hotel Room Reservation line history"""
        reservation_line_obj = self.env["hotel.room.reservation.line"]
        room_obj = self.env["hotel.room"]
        prod_id = vals.get("product_id") or self.product_id.id
        checkin = vals.get("checkin_date") or self.checkin_date
        checkout = vals.get("checkout_date") or self.checkout_date

        is_reserved = self.is_reserved
        if prod_id and is_reserved:
            prod_room = room_obj.search([("product_id", "=", prod_id)], limit=1)
            if self.product_id and self.checkin_date and self.checkout_date:
                old_prod_room = room_obj.search(
                    [("product_id", "=", self.product_id.id)], limit=1
                )
                if prod_room and old_prod_room:
                    # Check for existing room lines.
                    rm_lines = reservation_line_obj.search(
                        [
                            ("room_id", "=", old_prod_room.id),
                            ("check_in", "=", self.checkin_date),
                            ("check_out", "=", self.checkout_date),
                        ]
                    )
                    if rm_lines:
                        rm_line_vals = {
                            "room_id": prod_room.id,
                            "check_in": checkin,
                            "check_out": checkout,
                        }
                        rm_lines.write(rm_line_vals)
        return super(HotelFolioLine, self).write(vals)


class HotelServiceLine(models.Model):

    _inherit = "hotel.service.line"

    @api.model
    def create(self, vals):
        # Create invoice line when add service in folio
        service = super(HotelServiceLine, self).create(vals)
        if service.folio_id and service.folio_id.hotel_invoice_id:
            invoice_state = service.folio_id.hotel_invoice_id.state
            folio_state = service.folio_id.state
            payments = (
                self.env["account.payment"]
                .search([])
                .filtered(
                    lambda pay: service.folio_id.reservation_id.folio_id.hotel_invoice_id.id
                    in pay.reconciled_invoice_ids.ids
                )
            )
            service.folio_id.reservation_id.set_folio_draft()

            invoice_line = (
                self.env["account.move.line"]
                .with_context(check_move_validity=False)
                .new(
                    {
                        "product_id": service.product_id.id,
                        "quantity": service.product_uom_qty,
                        "price_unit": service.price_unit,
                    }
                )
            )
            invoice_line.with_context(check_move_validity=False)._onchange_product_id()
            invoice_line.with_context(
                check_move_validity=False
            ).price_unit = service.price_unit
            invoice_line.with_context(
                check_move_validity=False
            ).tax_ids = service.tax_id
            service.folio_id.hotel_invoice_id.with_context(
                check_move_validity=False
            ).invoice_line_ids += invoice_line
            # update discount and returnable amount in folio and invoice
            service.folio_id.reservation_id.update_discount_insurance_returnable_folio(
                (
                    service.folio_id.reservation_id.discount
                    + service.folio_id.reservation_id.discount_change_room
                ),
                service.folio_id.reservation_id.returnable_amount,
                False,
            )
            service.folio_id.reservation_id.post_folio_invoice(
                folio_state, invoice_state, payments
            )
        return service



# # See LICENSE file for full copyright and licensing details.

# from odoo import api, fields, models


# class HotelFolio(models.Model):

#     _inherit = "hotel.folio"
#     _order = "reservation_id desc"

#     reservation_id = fields.Many2one(
#         "hotel.reservation", "Reservation", ondelete="restrict"
#     )
#     duration = fields.Integer(related="reservation_id.duration", store=1)
#     reservation_type = fields.Selection(
#         related="reservation_id.reservation_type", store=1
#     )
#     room_rate = fields.Float(related="reservation_id.room_rate", store=1)
#     total_room_rate = fields.Float(related="reservation_id.total_room_rate", store=1)
#     discount = fields.Float(related="reservation_id.discount", store=1)
#     insurance = fields.Float(related="reservation_id.insurance", store=1)
#     taxes_amount = fields.Float(related="reservation_id.taxes_amount", store=1)
#     taxed_total_rate = fields.Float(related="reservation_id.taxed_total_rate", store=1)
#     total_cost = fields.Float(related="reservation_id.total_cost", store=1)
#     final_cost = fields.Float(related="reservation_id.final_cost", store=1)
#     rent = fields.Selection(related="reservation_id.rent", store=1)
#     payments_count = fields.Float(related="reservation_id.payments_count", store=1)
#     balance = fields.Float(related="reservation_id.balance", store=1)
#     service_amount = fields.Float(
#         string="Services", compute="_compute_service_amount", store=1
#     )
#     service_tax = fields.Float(
#         string="Services Tax", compute="_compute_service_amount", store=1
#     )
#     is_returnable = fields.Boolean(related="reservation_id.is_returnable", store=1)
#     returnable_amount = fields.Float(
#         related="reservation_id.returnable_amount", store=1
#     )

#     def write(self, vals):
#         res = super(HotelFolio, self).write(vals)
#         reservation_line_obj = self.env["hotel.room.reservation.line"]
#         for folio in self:
#             reservations = reservation_line_obj.search(
#                 [("reservation_id", "=", folio.reservation_id.id)]
#             )
#             if len(reservations) == 1:
#                 # Create reservation line in room
#                 for room in folio.reservation_id.reservation_line.mapped("room_id"):
#                     vals = {
#                         "room_id": room.id,
#                         "check_in": folio.checkin_date,
#                         "check_out": folio.checkout_date,
#                         "state": "assigned",
#                         "reservation_id": folio.reservation_id.id,
#                     }
#                     reservations.write(vals)
#         return res

#     def _update_folio_line(self, folio_id):
#         """Update folio lines"""
#         folio_room_line_obj = self.env["folio.room.line"]
#         hotel_room_obj = self.env["hotel.room"]
#         for rec in folio_id:
#             for room_rec in rec.room_line_ids:
#                 room = hotel_room_obj.search(
#                     [("product_id", "=", room_rec.product_id.id)], limit=1
#                 )
#                 room.write({"isroom": False})
#                 # Create folio romm line with reservation line
#                 vals = {
#                     "room_id": room.id,
#                     "check_in": rec.checkin_date,
#                     "check_out": rec.checkout_date,
#                     "folio_id": rec.id,
#                     "reservation_line_id": room_rec.reservation_line_id.id,
#                 }
#                 folio_room_line_obj.create(vals)

#     @api.depends("service_line_ids", "service_line_ids.price_subtotal")
#     def _compute_service_amount(self):
#         """Calculate service amount and service taxes"""
#         for folio in self:
#             taxes_amount = 0
#             for service_line in folio.service_line_ids:
#                 taxes = service_line.tax_id.compute_all(
#                     service_line.price_unit,
#                     service_line.currency_id,
#                     service_line.product_uom_qty,
#                     product=service_line.product_id,
#                 )
#                 taxes_amount += sum(
#                     tax.get("amount", 0.0) for tax in taxes.get("taxes", [])
#                 )
#             folio.service_amount = sum(folio.service_line_ids.mapped("price_subtotal"))
#             folio.service_tax = taxes_amount


# class HotelFolioLine(models.Model):

#     _inherit = "hotel.folio.line"

#     reservation_line_id = fields.Many2one("hotel.reservation.line", "Reservation Line")

#     @api.onchange("checkin_date", "checkout_date")
#     def _onchange_checkin_checkout_dates(self):
#         res = super(HotelFolioLine, self)._onchange_checkin_checkout_dates()
#         avail_prod_ids = []
#         for room in self.env["hotel.room"].search([]):
#             assigned = False
#             for line in room.room_reservation_line_ids.filtered(
#                 lambda l: l.status != "cancel"
#             ):
#                 if self.checkin_date and line.check_in and self.checkout_date:
#                     if (self.checkin_date <= line.check_in <= self.checkout_date) or (
#                         self.checkin_date <= line.check_out <= self.checkout_date
#                     ):
#                         assigned = True
#                     elif (line.check_in <= self.checkin_date <= line.check_out) or (
#                         line.check_in <= self.checkout_date <= line.check_out
#                     ):
#                         assigned = True
#             if not assigned:
#                 avail_prod_ids.append(room.product_id.id)
#         return res

#     def write(self, vals):
#         """
#         Overrides orm write method.
#         @param self: The object pointer
#         @param vals: dictionary of fields value.
#         Update Hotel Room Reservation line history"""
#         reservation_line_obj = self.env["hotel.room.reservation.line"]
#         room_obj = self.env["hotel.room"]
#         prod_id = vals.get("product_id") or self.product_id.id
#         checkin = vals.get("checkin_date") or self.checkin_date
#         checkout = vals.get("checkout_date") or self.checkout_date

#         is_reserved = self.is_reserved
#         if prod_id and is_reserved:
#             prod_room = room_obj.search([("product_id", "=", prod_id)], limit=1)
#             if self.product_id and self.checkin_date and self.checkout_date:
#                 old_prod_room = room_obj.search(
#                     [("product_id", "=", self.product_id.id)], limit=1
#                 )
#                 if prod_room and old_prod_room:
#                     # Check for existing room lines.
#                     rm_lines = reservation_line_obj.search(
#                         [
#                             ("room_id", "=", old_prod_room.id),
#                             ("check_in", "=", self.checkin_date),
#                             ("check_out", "=", self.checkout_date),
#                         ]
#                     )
#                     if rm_lines:
#                         rm_line_vals = {
#                             "room_id": prod_room.id,
#                             "check_in": checkin,
#                             "check_out": checkout,
#                         }
#                         rm_lines.write(rm_line_vals)
#         return super(HotelFolioLine, self).write(vals)


# class HotelServiceLine(models.Model):

#     _inherit = "hotel.service.line"

#     @api.model
#     def create(self, vals):
#         # Create invoice line when add service in folio
#         service = super(HotelServiceLine, self).create(vals)
#         if service.folio_id and service.folio_id.hotel_invoice_id:
#             invoice_state = service.folio_id.hotel_invoice_id.state
#             folio_state = service.folio_id.state
#             payments = (
#                 self.env["account.payment"]
#                 .search([])
#                 .filtered(
#                     lambda pay: service.folio_id.reservation_id.folio_id.hotel_invoice_id.id
#                     in pay.reconciled_invoice_ids.ids
#                 )
#             )
#             service.folio_id.reservation_id.set_folio_draft()

#             invoice_line = (
#                 self.env["account.move.line"]
#                 .with_context(check_move_validity=False)
#                 .new(
#                     {
#                         "product_id": service.product_id.id,
#                         "quantity": service.product_uom_qty,
#                         "price_unit": service.price_unit,
#                     }
#                 )
#             )
#             invoice_line.with_context(check_move_validity=False)._onchange_product_id()
#             invoice_line.with_context(
#                 check_move_validity=False
#             ).price_unit = service.price_unit
#             invoice_line.with_context(
#                 check_move_validity=False
#             ).tax_ids = service.tax_id
#             service.folio_id.hotel_invoice_id.with_context(
#                 check_move_validity=False
#             ).invoice_line_ids += invoice_line
#             # update discount and returnable amount in folio and invoice
#             service.folio_id.reservation_id.update_discount_insurance_returnable_folio(
#                 (
#                     service.folio_id.reservation_id.discount
#                     + service.folio_id.reservation_id.discount_change_room
#                 ),
#                 service.folio_id.reservation_id.returnable_amount,
#                 False,
#             )
#             service.folio_id.reservation_id.post_folio_invoice(
#                 folio_state, invoice_state, payments
#             )
#         return service



