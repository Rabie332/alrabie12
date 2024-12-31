from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PurchaseReportWizard(models.TransientModel):
    _name = "purchase.report.wizard"
    _description = "Purchase report"

    date_from = fields.Date(string="Date from", required=1)
    date_to = fields.Date(string="Date to", required=1)

    def print_report(self):
        data = {"ids": [self.id]}
        return self.env.ref("purchase_request.purchase_requests_report").report_action(
            self, data=data
        )

    @api.onchange("date_from", "date_to")
    def _onchange_dates(self):
        """Check date from and date to."""
        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise ValidationError(_("Date To must be greater than date from."))
