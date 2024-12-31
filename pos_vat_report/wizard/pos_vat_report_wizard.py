from odoo import fields, models


class PosVatReportWizard(models.TransientModel):
    _name = "pos.vat.report.wizard"
    _description = "POS vat report"

    date_from = fields.Date(string="Date from", required=1)
    date_to = fields.Date(string="Date to", required=1)
    pos_id = fields.Many2one("pos.config", string="Point of sale")

    def print_report(self):
        data = {"ids": [self.id], "form": self.read()[0]}
        return self.env.ref("pos_vat_report.action_pos_vat_report").report_action(
            self, data=data
        )
