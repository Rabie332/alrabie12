from odoo import api, models


class ClearanceRequestReport(models.AbstractModel):
    _name = "report.clearance_reports.clearance_request_report"
    _description = "Clearance request Report"

    def _get_lines(self, record):
        domain = []
        if record.date_from:
            domain = [("date", ">=", record.date_from)]
        if record.date_to:
            domain.append(("date", "<=", record.date_to))
        if record.state:
            domain.append(("state", "=", record.state))
        if record.partner_id:
            domain.append(("partner_id", "=", record.partner_id.id))
        clearance_ids = self.env["clearance.request"].search(domain, order="id desc")
        return clearance_ids

    @api.model
    def _get_report_values(self, docids, data=None):
        """Get report values."""
        ids = data.get("ids", [])
        docs = self.env["clearance.request.wizard"].browse(ids)
        return {
            "doc_ids": ids,
            "doc_model": "clearance.request.wizard",
            "docs": docs,
            "get_lines": self._get_lines,
        }
