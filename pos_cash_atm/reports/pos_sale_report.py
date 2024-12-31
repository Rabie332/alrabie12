import pytz
from pytz import timezone

from odoo import api, fields, models


class PosSaleReportTemplate(models.AbstractModel):
    _name = "report.pos_cash_atm.pos_sale_report_template"
    _description = "Template Report of sale"

    @api.model
    def _get_report_values(self, doc_ids, data=None):
        report = self.env["ir.actions.report"]._get_report_from_name(
            "pos_cash_atm.pos_sale_report_template"
        )
        return {
            "doc_ids": doc_ids or data["form"]["session_ids"],
            "doc_model": report.model,
            "docs": self.env["pos.session"].browse(
                doc_ids or data["form"]["session_ids"]
            ),
            "data": data,
        }


class PosSaleReport(models.TransientModel):
    _name = "pos.sale.report"
    _description = "Z-Report Backend"

    @api.model
    def _get_report_values(self, docids, data=None):
        if self.env.user and self.env.user.tz:
            tz = self.env.user.tz
            tz = timezone(tz)
        else:
            tz = pytz.utc
        report = self.env["ir.actions.report"]._get_report_from_name(
            "pos_cash_atm.pos_sale_report_template"
        )
        return {
            "doc_ids": self.env["pos.sale.report"].browse(data["ids"]),
            "doc_model": report.model,
            "docs": self.env["pos.session"].browse(data["form"]["session_ids"]),
            "data": data,
            "tz": tz,
        }

    def print_receipt(self):
        datas = {
            "ids": self._ids,
            "form": self.read()[0],
            "model": "pos.sale.report",
        }
        return self.env.ref("pos_cash_atm.report_pos_sales_pdf").report_action(
            self, data=datas
        )

    session_ids = fields.Many2many(
        "pos.session",
        "pos_sale_report_session_rel",
        "wizard_id",
        "session_id",
        string="Session(s)",
    )
