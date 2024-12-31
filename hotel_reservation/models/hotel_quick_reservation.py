# See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class QuickRoomReservation(models.Model):
    _name = "quick.room.reservation"
    _description = "Quick Room Reservation"
    _rec_name = "partner_id"

    partner_id = fields.Many2one(
        "res.partner", "Customer", domain="[('is_guest', '=', True)]"
    )
    check_in = fields.Datetime("Check In", required=True)
    check_out = fields.Datetime("Check Out", required=True)
    room_id = fields.Many2one("hotel.room", "Room", required=True)
    company_id = fields.Many2one(
        "res.company", "Hotel", required=True, default=lambda self: self.env.company
    )
    partner_invoice_id = fields.Many2one("res.partner", "Invoice Address")
    partner_order_id = fields.Many2one("res.partner", "Ordering Contact")
    partner_shipping_id = fields.Many2one(
        "res.partner",
        "Delivery Address",
    )
    adults = fields.Integer("Adults")
    source_id = fields.Many2one("hotel.reservation.source", string="Source Reservation")
    reason_id = fields.Many2one("reservation.visit.reason", string="Visit Reason")
    is_returnable = fields.Boolean(
        string="Returnable",
    )
    returnable_percentage = fields.Float(
        string="Percentage ",
    )
    source_number = fields.Char(
        string="Reservation source number",
    )
    reservation_id = fields.Many2one("hotel.reservation", string="Reservation")
    housekeeping_id = fields.Many2one("hotel.housekeeping", string="Housekeeping")
    under_maintenance = fields.Boolean(string="Under Maintenance")
    maintenance_type_id = fields.Many2one(
        "hotel.maintenance.type", related="housekeeping_id.maintenance_type_id"
    )
    current_date = fields.Date("Today's Date", related="housekeeping_id.current_date")
    inspector_id = fields.Many2one(
        "res.users", "Inspector", related="housekeeping_id.inspector_id"
    )
    inspect_date_time = fields.Datetime(
        "Inspect Date Time", related="housekeeping_id.inspect_date_time"
    )

    @api.onchange("check_out", "check_in")
    def _on_change_check_out(self):
        """
        When you change checkout or checkin it will check whether
        Checkout date should be greater than Checkin date
        and update dummy field
        -----------------------------------------------------------
        @param self: object pointer
        @return: raise warning depending on the validation
        """
        if (self.check_out and self.check_in) and (self.check_out < self.check_in):
            raise ValidationError(
                _("Checkout date should be greater than Checkin date.")
            )

    @api.onchange("partner_id")
    def _onchange_partner_id_res(self):
        """
        When you change partner_id it will update the partner_invoice_id,
        partner_shipping_id of the hotel reservation as well
        ---------------------------------------------------------------------
        @param self: object pointer
        """
        if not self.partner_id:
            self.update(
                {
                    "partner_invoice_id": False,
                    "partner_shipping_id": False,
                    "partner_order_id": False,
                }
            )
        else:
            addr = self.partner_id.address_get(["delivery", "invoice", "contact"])
            self.update(
                {
                    "partner_invoice_id": addr["invoice"],
                    "partner_shipping_id": addr["delivery"],
                    "partner_order_id": addr["contact"],
                }
            )

    @api.model
    def default_get(self, fields):
        """
        To get default values for the object.
        @param self: The object pointer.
        @param fields: List of fields for which we want default values
        @return: A dictionary which of fields with values.
        """
        res = super(QuickRoomReservation, self).default_get(fields)
        keys = self._context.keys()
        if "date" in keys:
            res.update({"check_in": self._context["date"]})
        if "room_id" in keys:
            roomid = self._context["room_id"]
            res.update({"room_id": int(roomid)})
        return res

    def room_reserve(self):
        """
        This method create a new record for hotel.reservation
        -----------------------------------------------------
        @param self: The object pointer
        @return: new record set for hotel reservation.
        """
        hotel_res_obj = self.env["hotel.reservation"]
        for res in self:
            reservation_id = hotel_res_obj.create(
                {
                    "partner_id": res.partner_id.id,
                    "partner_invoice_id": res.partner_invoice_id.id,
                    "partner_order_id": res.partner_order_id.id,
                    "partner_shipping_id": res.partner_shipping_id.id,
                    "checkin": res.check_in,
                    "checkout": res.check_out,
                    "company_id": res.company_id.id,
                    "adults": res.adults,
                    "source_id": res.source_id.id,
                    "reason_id": res.reason_id.id,
                    "is_returnable": res.is_returnable,
                    "returnable_percentage": res.returnable_percentage,
                    "source_number": res.source_number,
                    "reservation_line": [
                        (
                            0,
                            0,
                            {
                                "room_id": res.room_id.id,
                                "name": res.room_id.name or " ",
                            },
                        )
                    ],
                }
            )
            if reservation_id:
                self.reservation_id = reservation_id.id
        return {"type": "ir.actions.client", "tag": "reload"}
