from odoo import api, models


class MaintenanceReport(models.AbstractModel):
    _name = "report.hotel_housekeeping.maintenance_several_report"
    _description = "Maintenance Report"

    def _get_lines(self, record):
        domain = [
            ("type", "=", "maintenance"),
            ("create_date", "<=", record.date_end),
            ("create_date", ">=", record.date_start),
        ]
        line_ids = self.env["hotel.housekeeping"].search(domain)
        return line_ids

    @api.model
    def _get_report_values(self, docids, data=None):
        """Get report values."""
        ids = data.get("ids", [])
        docs = self.env["hotel.housekeeping.maintenance.wizard"].browse(ids)
        return {
            "doc_ids": ids,
            "doc_model": "hotel.housekeeping.maintenance.wizard",
            "docs": docs,
            "get_lines": self._get_lines,
        }
