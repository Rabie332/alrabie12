from odoo import api, fields, models
from odoo.tools.misc import get_lang


class AccountingReport(models.TransientModel):
    _name = "accounting.reporting"
    _inherit = "account.common.report"
    _description = "Accounting Reporting"

    @api.model
    def _get_account_report(self):
        reports = []
        if self._context.get("active_id"):
            menu = self.env["ir.ui.menu"].browse(self._context.get("active_id")).name
            reports = self.env["account.financial.report"].search(
                [("name", "ilike", menu)]
            )
        return reports and reports[0] or False

    enable_filter = fields.Boolean(string="Enable Comparison")
    target_move = fields.Selection(
        [("posted", "All Posted Entries"), ("all", "All Entries")],
        string="Target Moves",
        required=True,
        default="posted",
    )
    account_report_id = fields.Many2one(
        "account.financial.report",
        string="Account Reports",
        required=True,
        default=_get_account_report,
    )
    analytic_account_ids = fields.Many2many(
        "account.analytic.account", string="Analytic accounts"
    )
    label_filter = fields.Char(
        string="Column Label",
        help="This label will be displayed on report to show the balance computed "
        "for the given comparison filter.",
    )
    filter_cmp = fields.Selection(
        [("filter_no", "No Filters"), ("filter_date", "Date")],
        string="Filter by",
        required=True,
        default="filter_no",
    )
    date_from_cmp = fields.Date(string="Start Date Compare")
    date_to_cmp = fields.Date(string="End Date Compare")
    debit_credit = fields.Boolean(
        string="Display Debit/Credit Columns",
        help="This option allows you to get more details about the way your balances "
        "are computed. Because it is space consuming, we do not allow to use it "
        "while doing a comparison.",
    )

    def _build_contexts(self, data):
        result = super()._build_contexts(data)
        result["analytic_account_ids"] = (
            "analytic_account_ids" in data["form"]
            and data["form"]["analytic_account_ids"]
            or False
        )
        return result

    def _build_comparison_context(self, data):
        result = {}
        result["journal_ids"] = (
            "journal_ids" in data["form"] and data["form"]["journal_ids"] or False
        )
        result["state"] = (
            "target_move" in data["form"] and data["form"]["target_move"] or ""
        )
        if data["form"]["filter_cmp"] == "filter_date":
            result["date_from"] = data["form"]["date_from_cmp"]
            result["date_to"] = data["form"]["date_to_cmp"]
            result["strict_range"] = True
        return result

    def _print_report(self, report_type):
        self.ensure_one()
        data = {}
        data["form"] = self.read(
            [
                "account_report_id",
                "date_from_cmp",
                "date_to_cmp",
                "journal_ids",
                "analytic_account_ids",
                "filter_cmp",
                "target_move",
                "enable_filter",
                "debit_credit",
                "date_from",
                "date_to",
                "company_id",
            ]
        )[0]
        used_context = self._build_contexts(data)
        data["form"]["used_context"] = dict(used_context, lang=get_lang(self.env).code)
        comparison_context = self._build_comparison_context(data)
        data["form"]["comparison_context"] = comparison_context
        if report_type == "xlsx":
            report_name = "a_b_s.report_financial_xlsx"
        else:
            report_name = "account_balance_sheet_report.report_financial"
        return (
            self.env["ir.actions.report"]
            .search(
                [("report_name", "=", report_name), ("report_type", "=", report_type)],
                limit=1,
            )
            .with_context(lang=self.env.lang)
            .report_action(self, data=data)
        )

    def button_export_html(self):
        self.ensure_one()
        report_type = "qweb-html"
        return self._export(report_type)

    def button_export_pdf(self):
        self.ensure_one()
        report_type = "qweb-pdf"
        return self._export(report_type)

    def button_export_xlsx(self):
        self.ensure_one()
        report_type = "xlsx"
        return self._export(report_type)

    def _export(self, report_type):
        """Default export is PDF."""
        return self._print_report(report_type)

    def _get_atr_from_dict(self, obj_id, data, key):
        try:
            return data[obj_id][key]
        except KeyError:
            return data[str(obj_id)][key]
