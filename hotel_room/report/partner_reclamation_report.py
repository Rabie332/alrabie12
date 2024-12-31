from odoo import api, models


class PartnerReclamationReport(models.AbstractModel):
    _name = "report.hotel_room.report_partner_reclamation_template"
    _description = "Partner Reclamation Report"

    def _get_lines(self, record):
        domain = [
            ("create_date", "<=", record.date_to),
            ("create_date", ">=", record.date_from),
        ]
        if record.state:
            domain += [("state", "=", record.state)]
        line_ids = self.env["partner.reclamation"].search(domain)
        return line_ids

    @api.model
    def _get_report_values(self, docids, data=None):
        """Get report values."""
        ids = data.get("ids", [])
        docs = self.env["partner.reclamation.wizard"].browse(ids)
        return {
            "doc_ids": ids,
            "doc_model": "partner.reclamation.wizard",
            "docs": docs,
            "get_lines": self._get_lines,
        }
