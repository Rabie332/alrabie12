from odoo import api, fields, models


class HotelReservationPaymentReportInvoice(models.TransientModel):
    _name = "hotel.reservation.payment.invoice.report"
    _description = "Hotel Reservation Payment Invoice Report"

    date_from = fields.Date("From", required=True)
    date_to = fields.Date("To", required=True)
    reservation_no = fields.Char("Reservation No")
    payment_name = fields.Char("Payment Name")
    invoice_name = fields.Char("Invoice Name")
    support_type_id = fields.Many2one("account.payment.support.type")
    payment_method_id = fields.Many2one(
        "account.payment.method", string="Payment Method"
    )

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
            .env.ref(
                "hotel_reservation_reports.reservation_payment_invoice_report_preview"
            )
            .report_action(self, data=data)
        )

    def print_payment_inbound_report(self):
        data = {"ids": [self.id], "form": self.read()[0]}
        return (
            self.with_context(payment_type=self._context.get("partner_type"))
            .env.ref(
                "hotel_reservation_reports.reservation_payment_invoice_report_preview"
            )
            .report_action(self, data=data)
        )

    def print_payment_invoice_report(self):
        data = {"ids": [self.id], "form": self.read()[0]}
        return (
            self.with_context(payment_type=self._context.get("partner_type"))
            .env.ref(
                "hotel_reservation_reports.reservation_payment_invoice_report_preview"
            )
            .report_action(self, data=data)
        )


class ResumeHotelReservationPaymentInvoice(models.AbstractModel):
    _name = "report.hotel_reservation_reports.report_payment_invoice"
    _description = "Hotel Reservation Payment Resume"

    def _get_lines(self, record):
        date_from = record.date_from
        date_to = record.date_to
        reservation_no = record.reservation_no
        payment_name = record.payment_name
        invoice_name = record.invoice_name
        support_type_id = record.support_type_id
        payment_method_id = record.payment_method_id
        domain = [
            ("date", "<=", date_to),
            ("date", ">=", date_from),
            ("reservation_id", "!=", False),
        ]
        if reservation_no:
            domain.append(("reservation_id.reservation_no", "=", reservation_no))
        if self._context.get("payment_type") == "invoice":
            if invoice_name:
                domain.append(("name", "=", invoice_name))
        if self._context.get("payment_type") != "invoice":
            if payment_name:
                domain.append(("name", "=", payment_name))
            if support_type_id:
                domain.append(("support_type_id", "=", support_type_id.id))
            if payment_method_id:
                domain.append(("payment_method_id", "=", payment_method_id.id))
        if self._context.get("payment_type") != "invoice":
            if self._context.get("payment_type") == "outbound":
                domain.append(("payment_type", "=", "outbound"))
            else:
                domain.append(("payment_type", "=", "inbound"))
            payments_invoices = self.env["account.payment"].search(domain)
        else:
            payments_invoices = self.env["account.move"].search(
                domain + [("move_type", "in", ("out_invoice", "in_invoice"))]
            )
        return payments_invoices

    @api.model
    def _get_report_values(self, docids, data=None):
        """Get report values."""
        ids = data.get("ids", [])
        docs = self.env["hotel.reservation.payment.invoice.report"].browse(ids)
        return {
            "doc_ids": ids,
            "doc_model": "hotel.reservation.payment.invoice.report",
            "docs": docs,
            "lang": self.env.user.lang,
            "get_lines": self._get_lines,
        }
