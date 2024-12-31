from odoo import api, models


class PurchaseRequestsReport(models.AbstractModel):
    _name = "report.purchase_request.purchase_requests_template"
    _description = "Purchase Requests Report"

    def _get_purchases(self, record):
        domain = [
            ("date", ">=", record.date_from),
            ("date", "<=", record.date_to),
        ]
        purchase_ids = self.env["purchase.request"].search(domain)
        return purchase_ids

    @api.model
    def _get_report_values(self, docids, data=None):
        """Get report values."""
        ids = data.get("ids", [])
        docs = self.env["purchase.report.wizard"].browse(ids)
        return {
            "doc_ids": ids,
            "doc_model": "purchase.report.wizard",
            "docs": docs,
            "get_purchases": self._get_purchases,
        }
