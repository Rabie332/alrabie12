import time

from odoo import api, fields, models
from odoo.osv import expression


class AttachmentSummaryReport(models.TransientModel):
    _name = "attachment.summary.report"
    _description = "Attachment Summary Report"

    date_from = fields.Date(
        string="Date from", default=lambda *a: time.strftime("%Y-%m-%d"), required=1
    )
    date_to = fields.Date(
        string="Date to", default=lambda *a: time.strftime("%Y-%m-%d"), required=1
    )
    type_id = fields.Many2one("ir.attachment.type", string="Type")
    folder_id = fields.Many2one("dms.folder", string="Folder")

    def print_report(self):
        """Print Report document summary‬."""
        data = {"ids": [self.id], "form": self.read([])[0]}
        return self.env.ref("dms.attachment_summary_report").report_action(
            self, data=data
        )


class AttachmentSummaryReportParser(models.AbstractModel):
    _name = "report.dms.attachments_summary_report"
    _description = "Attachment Summary Report Parser"

    def _get_lines(self, data):
        type_id = data["type_id"] and data["type_id"][0] or False
        folder_id = data["folder_id"] and data["folder_id"][0] or False
        domain = [
            ("create_date", ">=", data["date_from"]),
            ("create_date", "<=", data["date_to"]),
            ("res_model", "not in", ["ir.ui.view", "Country", "ir.ui.menu"]),
            ("res_field", "=", False),
            ("res_id", "=", False),
            ("create_uid", "not in", [1, 4]),
            ("extension", "not in", [".scss", ".ics", ".a"]),
        ]
        # Todo: Check why rule doesn't work in ir.attachment here
        domain = expression.AND(
            [
                domain,
                [
                    "|",
                    ("company_id", "=", False),
                    ("company_id", "in", self.env.user.company_ids.ids),
                ],
            ]
        )
        if type_id:
            domain.append(("type_id", "=", type_id))
        if folder_id:
            domain.append(("folder_id", "=", folder_id))
        attachments = self.env["ir.attachment"].search(domain)
        return attachments

    @api.model
    def _get_report_values(self, docids, data=None):
        """Get report values."""
        data = data if data is not None else {}
        ids = data.get("ids", [])
        docs = self.env["attachment.summary.report"].browse(ids)
        return {
            "doc_ids": docids,
            "doc_model": "attachment.summary.report",
            "data": data,
            "docs": docs,
            "lang": "ar_SY",
            "get_lines": self._get_lines,
        }
