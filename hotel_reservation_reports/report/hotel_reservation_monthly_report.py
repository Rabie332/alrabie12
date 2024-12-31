from datetime import date

from odoo import api, fields, models


class HotelReservationMonthlyReport(models.TransientModel):
    _name = "hotel.reservation.monthly.report"
    _description = "Hotel Reservation monthly Report"

    month = fields.Selection(
        [
            ("1", "1"),
            ("2", "2"),
            ("3", "3"),
            ("4", "4"),
            ("5", "5"),
            ("6", "6"),
            ("7", "7"),
            ("8", "8"),
            ("9", "9"),
            ("10", "10"),
            ("11", "11"),
            ("12", "12"),
        ],
        "Month",
        required=1,
        default=1,
    )
    report_type = fields.Selection(
        [
            ("collection", "Collection of reservations"),
            ("total", "Total Collection"),
        ],
        default="collection",
    )

    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, record.month))
        return result

    def print_monthly_report(self):
        data = {"ids": [self.id], "form": self.read()[0]}
        if self.report_type:
            report = self.with_context(monthly_type=self.report_type).env.ref(
                "hotel_reservation_reports.reservation_monthly_collection_report_preview"
            )
        else:
            report = self.with_context(monthly_type=self.report_type).env.ref(
                "hotel_reservation_reports.reservation_monthly_total_report_preview"
            )
        return report.report_action(self, data=data)


class ResumeHotelReservationMonthly(models.AbstractModel):
    _name = "report.hotel_reservation_reports.report_reservation_monthly"
    _description = "Hotel Reservation monthly Resume"

    def _get_lines(self, record):
        month = record.month
        reservations = self.env["hotel.reservation"].search([])
        reservations = reservations.filtered(
            lambda reservation: int(reservation.create_date.month) == int(month)
            and int(reservation.create_date.year) == int(date.today().year)
        )
        payments_outbound = (
            self.env["account.payment"]
            .search([("payment_type", "=", "outbound"), ("state", "!=", "cancel")])
            .filtered(
                lambda payment_outbound: int(payment_outbound.create_date.month)
                == int(month)
                and int(payment_outbound.create_date.year) == int(date.today().year)
            )
        )
        payments_inbound = (
            self.env["account.payment"]
            .search([("payment_type", "=", "inbound"), ("state", "!=", "cancel")])
            .filtered(
                lambda payment_inbound: int(payment_inbound.create_date.month)
                == int(month)
                and int(payment_inbound.create_date.year) == int(date.today().year)
            )
        )
        payments_outbound_posted = (
            self.env["account.payment"]
            .search([("payment_type", "=", "outbound"), ("state", "=", "posted")])
            .filtered(
                lambda payment_outbound: int(payment_outbound.write_date.month)
                == int(month)
                and int(payment_outbound.write_date.year) == int(date.today().year)
            )
        )
        payments_inbound_posted = (
            self.env["account.payment"]
            .search([("payment_type", "=", "inbound"), ("state", "=", "posted")])
            .filtered(
                lambda payment_inbound: int(payment_inbound.write_date.month)
                == int(month)
                and int(payment_inbound.write_date.year) == int(date.today().year)
            )
        )
        return (
            reservations,
            payments_outbound,
            payments_inbound,
            payments_outbound_posted,
            payments_inbound_posted,
        )

    @api.model
    def _get_report_values(self, docids, data=None):
        """Get report values."""
        ids = data.get("ids", [])
        docs = self.env["hotel.reservation.monthly.report"].browse(ids)
        return {
            "doc_ids": ids,
            "doc_model": "hotel.reservation.monthly.report",
            "docs": docs,
            "lang": self.env.user.lang,
            "get_lines": self._get_lines,
        }
