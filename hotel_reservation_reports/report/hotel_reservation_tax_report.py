from odoo import api, fields, models


class HotelReservationTaxReport(models.TransientModel):
    _name = "hotel.reservation.tax.report"
    _description = "Hotel Reservation tax Report"

    @api.model
    def _get_domain(self):
        """Get rooms domains"""
        reservations = self.env["hotel.reservation"].search([])
        return [
            (
                "id",
                "in",
                reservations.mapped(
                    "hotel_invoice_id.invoice_line_ids.tax_ids.tax_group_id"
                ).ids,
            )
        ]

    date_from = fields.Date("From", required=True)
    date_to = fields.Date("To", required=True)
    tax_group_id = fields.Many2one(
        "account.tax.group", string="Taxes", domain=_get_domain, required=1
    )

    def name_get(self):
        result = []
        for record in self:
            name = "{}-{} ".format(record.date_from, record.date_to)
            result.append((record.id, name))
        return result

    def print_tax_report(self):
        data = {"ids": [self.id], "form": self.read()[0]}
        return self.env.ref(
            "hotel_reservation_reports.reservation_tax_report_preview"
        ).report_action(self, data=data)


class ResumeHotelReservationTax(models.AbstractModel):
    _name = "report.hotel_reservation_reports.report_reservation_tax"
    _description = "Hotel Reservation tax Resume"

    def _get_lines(self, record):
        date_from = record.date_from
        date_to = record.date_to
        tax_group_id = record.tax_group_id
        reservations = self.env["hotel.reservation"].search(
            [
                ("checkout", "<=", date_to),
                ("checkin", ">=", date_from),
                ("hotel_invoice_id.move_type", "=", "out_invoice"),
            ]
        )
        reservations.filtered(
            lambda reservation: tax_group_id.id
            in reservation.hotel_invoice_id.invoice_line_ids.mapped(
                "tax_ids.tax_group_id"
            ).ids
        )
        return reservations.mapped("hotel_invoice_id.invoice_line_ids")

    @api.model
    def _get_report_values(self, docids, data=None):
        """Get report values."""
        ids = data.get("ids", [])
        docs = self.env["hotel.reservation.tax.report"].browse(ids)
        return {
            "doc_ids": ids,
            "doc_model": "hotel.reservation.tax.report",
            "docs": docs,
            "lang": self.env.user.lang,
            "get_lines": self._get_lines,
        }
