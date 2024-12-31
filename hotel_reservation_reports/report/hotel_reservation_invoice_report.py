from odoo import api, fields, models


class HotelReservationInvoiceReport(models.TransientModel):
    _name = "hotel.reservation.invoice.report"
    _description = "Hotel Reservation invoice Report"

    date_from = fields.Date("From", required=True)
    date_to = fields.Date("To", required=True)
    create_date_from = fields.Datetime("Create Date From")
    create_date_to = fields.Datetime("Create Date To")
    reservation_no = fields.Char("Reservation No")
    partner_id = fields.Many2one(
        "res.partner", "Customer", domain="[('is_guest', '=', True)]"
    )
    room_no = fields.Char("Room No")

    def name_get(self):
        result = []
        for record in self:
            name = "{}-{} ".format(record.date_from, record.date_to)
            result.append((record.id, name))
        return result

    def print_invoice_report(self):
        data = {"ids": [self.id], "form": self.read()[0]}
        return self.env.ref(
            "hotel_reservation_reports.reservation_invoice_report_preview"
        ).report_action(self, data=data)


class ResumeHotelReservationInvoice(models.AbstractModel):
    _name = "report.hotel_reservation_reports.report_reservation_invoice"
    _description = "Hotel Reservation invoice Resume"

    def _get_lines(self, record):
        date_from = record.date_from
        date_to = record.date_to
        create_date_from = record.create_date_from
        create_date_to = record.create_date_to
        reservation_no = record.reservation_no
        room_no = record.room_no
        partner_id = record.partner_id
        domain = [
            ("checkout", "<=", date_to),
            ("checkin", ">=", date_from),
            ("hotel_invoice_id.move_type", "=", "out_invoice"),
        ]
        if create_date_from and create_date_to:
            domain.append(("hotel_invoice_id.create_date", "<=", create_date_to))
            domain.append(("hotel_invoice_id.create_date", ">=", create_date_from))
        if reservation_no:
            domain.append(("reservation_no", "=", reservation_no))
        if partner_id:
            domain.append(("partner_id", "=", partner_id.id))
        reservations = self.env["hotel.reservation"].search(domain)
        if room_no:
            reservations.filtered(
                lambda reservation: room_no
                in reservation.reservation_line.mapped("room_id.name")
            )
        return reservations.mapped("hotel_invoice_id")

    @api.model
    def _get_report_values(self, docids, data=None):
        """Get report values."""
        ids = data.get("ids", [])
        docs = self.env["hotel.reservation.invoice.report"].browse(ids)
        return {
            "doc_ids": ids,
            "doc_model": "hotel.reservation.invoice.report",
            "docs": docs,
            "lang": self.env.user.lang,
            "get_lines": self._get_lines,
        }
