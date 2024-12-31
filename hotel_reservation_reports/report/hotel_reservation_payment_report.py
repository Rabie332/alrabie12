from odoo import api, fields, models


class HotelReservationPaymentReport(models.TransientModel):
    _name = "hotel.reservation.payment.report"
    _description = "Hotel Reservation Payment Report"

    date_from = fields.Datetime("From", required=True)
    date_to = fields.Datetime("To", required=True)
    user_id = fields.Many2one("res.users", string="User")

    def name_get(self):
        result = []
        for record in self:
            name = "{}-{} ".format(record.date_from, record.date_to)
            result.append((record.id, name))
        return result

    def print_payment_outbound_report(self):
        data = {"ids": [self.id], "form": self.read()[0]}
        return (
            self.with_context(payment_type=self._context.get("partner_type"))
            .env.ref("hotel_reservation_reports.reservation_payment_report_preview")
            .report_action(self, data=data)
        )

    def print_payment_inbound_report(self):
        data = {"ids": [self.id], "form": self.read()[0]}
        return (
            self.with_context(payment_type=self._context.get("partner_type"))
            .env.ref("hotel_reservation_reports.reservation_payment_report_preview")
            .report_action(self, data=data)
        )


class ResumeHotelReservationPayment(models.AbstractModel):
    _name = "report.hotel_reservation_reports.report_reservation_payment"
    _description = "Hotel Reservation Payment Resume"

    def _get_lines(self, record):
        date_from = record.date_from
        date_to = record.date_to
        user_id = record.user_id
        domain = [
            ("create_date", "<=", date_to),
            ("create_date", ">=", date_from),
            ("reservation_id", "!=", False),
        ]
        if user_id:
            domain.append(("create_uid", "=", user_id))
        if self._context.get("payment_type") == "outbound":
            domain.append(("payment_type", "=", "outbound"))
        else:
            domain.append(("payment_type", "=", "inbound"))
        payments = self.env["account.payment"].search(domain)
        return payments

    @api.model
    def _get_report_values(self, docids, data=None):
        """Get report values."""
        ids = data.get("ids", [])
        docs = self.env["hotel.reservation.payment.report"].browse(ids)
        return {
            "doc_ids": ids,
            "doc_model": "hotel.reservation.payment.report",
            "docs": docs,
            "lang": self.env.user.lang,
            "get_lines": self._get_lines,
        }
