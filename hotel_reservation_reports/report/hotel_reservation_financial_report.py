from odoo import api, fields, models


class HotelReservationFinancialReport(models.TransientModel):
    _name = "hotel.reservation.financial.report"
    _description = "Hotel Reservation Financial Report"

    date_from = fields.Datetime("From", required=True)
    date_to = fields.Datetime("To", required=True)
    user_id = fields.Many2one("res.users", string="User")
    reservation_id = fields.Many2one("hotel.reservation", "Reservation", ondelete="restrict")
    


    def print_reservation_financial_report_preview(self):
        data = {"ids": [self.id], "form": self.read()[0]}
        return self.env.ref(
            "hotel_reservation_reports.reservation_financial_report_preview"
        ).report_action(self, data=data)


class ResumeHotelReservationFinancial(models.AbstractModel):
    _name = "report.hotel_reservation_reports.report_reservation_financial"
    _description = "Hotel Reservation Financial Resume"

    def _get_lines(self, record):
        domain = [
            ("create_date", "<=", record.date_to),
            ("create_date", ">=", record.date_from),
            ("reservation_id", "!=", False),
        ]
        if record.user_id:
            domain.append(("create_uid", "=", record.user_id.id))
        if record.reservation_id:
            domain.append(("reservation_id", "=", record.reservation_id.id))
        payments = self.env["account.payment"].search(domain)
        return payments
    
    def _get_total_inbound(self, payments):
        total_inbound_payments = 0
        for payment in payments:
            total_inbound = payment.reservation_id.total_inbound_payments or 0
            total_inbound_payments += total_inbound
        return total_inbound_payments

    

    def _get_total_outbound(self, payments):
        total_outbound_payments = 0
        for payment in payments:
            total_outbound = payment.reservation_id.total_outbound_payments or 0
            total_outbound_payments += total_outbound
        return total_outbound_payments


    def _get_total_insurance(self, payments):
        total_insurance = 0
        for payment in payments:
            insurance = payment.reservation_id.total_inbound_insurance or 0
            return_insurance_amount = payment.reservation_id.total_outbound_insurance or 0
            total_insurance +=  insurance - return_insurance_amount
        return total_insurance

    @api.model
    def _get_report_values(self, docids, data=None):
        ids = data.get("ids", [])
        docs = self.env["hotel.reservation.financial.report"].browse(ids)
        payments = self._get_lines(docs)
        total_inbound = self._get_total_inbound(payments)
        total_outbound = self._get_total_outbound(payments)
        total_insurance = self._get_total_insurance(payments)  # Calculate total insurance
        net = total_inbound - total_outbound
        total_fund = net + total_insurance
        return {
            "doc_ids": ids,
            "doc_model": "hotel.reservation.financial.report",
            "docs": docs,
            "get_lines": self._get_lines,
            "total_inbound": total_inbound,
            "total_outbound": total_outbound,
            "total_insurance": total_insurance,  
            "net": net,
            "total_fund": total_fund,
        }