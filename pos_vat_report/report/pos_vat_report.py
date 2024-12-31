from odoo import api, models


class PosVatReport(models.AbstractModel):
    _name = "report.pos_vat_report.pos_vat_report"
    _description = "POS VAT Report"

    def _get_lines(self, record):
        date_from = record.date_from
        date_to = record.date_to
        domain = [
            ("date_order", "<=", date_to),
            ("date_order", ">=", date_from),
            ("state", "not in", ["draft", "cancel"]),
        ]
        if record.pos_id:
            domain.append(("config_id", "=", record.pos_id.id))
        orders = self.env["pos.order"].search(domain)
        return orders

    @api.model
    def _get_report_values(self, docids, data=None):
        """Get report values."""
        ids = data.get("ids", [])
        docs = self.env["pos.vat.report.wizard"].browse(ids)
        return {
            "doc_ids": ids,
            "doc_model": "pos.vat.report.wizard",
            "docs": docs,
            "get_lines": self._get_lines,
        }
