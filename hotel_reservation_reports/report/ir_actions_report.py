# Copyright 2020 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    @api.model
    def _prepare_account_financial_report_context(self, data):
        return (
            dict(self.env.context or {}, lang=self.env.user.lang)
            if self.env.user.lang
            else False
        )

    @api.model
    def _render_qweb_html(self, docids, data=None):
        context = self._prepare_account_financial_report_context(data)
        obj = self.with_context(context) if context else self
        return super(IrActionsReport, obj)._render_qweb_html(docids, data)

    @api.model
    def _render_xlsx(self, docids, data):
        context = self._prepare_account_financial_report_context(data)
        obj = self.with_context(context) if context else self
        return super(IrActionsReport, obj)._render_xlsx(docids, data)
