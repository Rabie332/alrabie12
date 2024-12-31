from odoo import fields, models


class ClearanceRequestWizard(models.TransientModel):
    _name = "clearance.request.wizard"
    _description = "Clearance Request Wizard"

    date_from = fields.Date(string="Date from", required=1)
    date_to = fields.Date(string="Date to", required=1)
    partner_id = fields.Many2one(
        "res.partner",
        string="Customer Name",
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("customs_clearance", "Customs Clearance"),
            ("customs_statement", "Customs Statement"),
            ("transport", "Transport"),
            ("delivery", " Receipt and Delivery"),
            ("delivery_done", "Delivery Done"),
            ("close", "Close deal"),
            ("canceled", "canceled"),
        ],
        string="State",
    )

    def print_report(self):
        data = {"ids": [self.id], "form": self.read()[0]}
        return self.env.ref(
            "clearance_reports.action_clearance_request_report"
        ).report_action(self, data=data)

    def print_clearance_xls_report(self):
        data = {"ids": [self.id], "form": self.read()[0]}
        return self.env.ref("clearance_reports.clearance_request_xlsx").report_action(
            self, data=data
        )
