from odoo import api, models


class AccountEntryReport(models.AbstractModel):
    _name = "report.account_move_report.account_entry_report_template"
    _description = "Entries Reports"

    def _get_lines(self, record):
        """Get entries based on dates and state."""
        date_from = record.date_from
        date_to = record.date_to
        domain = [
            ("date", "<=", date_to),
            ("date", ">=", date_from),
        ]
        if record.is_posted_entry:
            domain.append(("state", "=", "posted"))
        entries = self.env["account.move"].search(domain)
        return entries

    @api.model
    def _get_report_values(self, docids, data=None):
        """Get report values."""
        ids = data.get("ids", [])
        docs = self.env["account.entry.report.wizard"].browse(ids)
        return {
            "doc_ids": ids,
            "doc_model": "account.entry.report.wizard",
            "data": data,
            "docs": docs,
            "lang": "ar_SY",
            "get_lines": self._get_lines,
        }
