from odoo import _, models
from odoo.exceptions import UserError


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    def _render_qweb_pdf(self, res_ids=None, data=None):
        """Check move and report are of entries."""
        if self.model == "account.move" and res_ids:
            entry_report = self.env.ref("account_move_report.report_account_move")
            if self == entry_report:
                moves = self.env["account.move"].browse(res_ids)
                if any(move.is_invoice(include_receipts=True) for move in moves):
                    raise UserError(_("Only entries could be printed."))

        return super()._render_qweb_pdf(res_ids=res_ids, data=data)
