from odoo import api, models


class HotelVerificationReport(models.AbstractModel):
    _name = "report.hotel.report_hotel_verification_template"
    _description = "Hotel Verification Report"

    def _get_lines(self, record):
        domain = [
            ("date", "<=", record.date_to),
            ("date", ">=", record.date_from),
        ]
        if record.type == "day":
            domain += [("type", "=", "day")]
        else:
            domain += [("type", "=", "night")]
        line_ids = self.env["hotel.verification"].search(domain)
        return line_ids

    @api.model
    def _get_report_values(self, docids, data=None):
        """Get report values."""
        ids = data.get("ids", [])
        docs = self.env["hotel.verification.wizard"].browse(ids)
        return {
            "doc_ids": ids,
            "doc_model": "hotel.verification.wizard",
            "docs": docs,
            "get_lines": self._get_lines,
        }
