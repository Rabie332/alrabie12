from odoo import api, models


class LostFoundReport(models.AbstractModel):
    _name = "report.hotel.report_hotel_lost_found_objects"
    _description = "Lost Found Report"

    def _get_lines(self, record):
        domain = []
        if record.date_type == "create_date":
            domain += [
                ("create_date", "<=", record.date_to),
                ("create_date", ">=", record.date_from),
            ]
        elif record.date_type == "delivery_date":
            domain += [
                ("delivery_date", "<=", record.date_to),
                ("delivery_date", ">=", record.date_from),
            ]
        else:
            domain += [
                ("found_date", "<=", record.date_to),
                ("found_date", ">=", record.date_from),
            ]
        if record.type == "lost":
            domain += [("type", "=", "lost")]
        else:
            domain += [("type", "=", "found")]
        line_ids = self.env["hotel.lost.found"].search(domain)
        return line_ids

    @api.model
    def _get_report_values(self, docids, data=None):
        """Get report values."""
        ids = data.get("ids", [])
        docs = self.env["hotel.lost.found.wizard"].browse(ids)
        return {
            "doc_ids": ids,
            "doc_model": "hotel.lost.found.wizard",
            "docs": docs,
            "get_lines": self._get_lines,
        }
