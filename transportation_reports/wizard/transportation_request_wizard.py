from odoo import fields, models, api

class TransportationRequestWizard(models.TransientModel):
    _name = "transportation.request.wizard"
    _description = "Transportation Request Wizard"

    transport_type = fields.Selection(
        string="Transport Type",
        selection=[
            ("warehouse", "Yard"),
            ("customer", "Customer site"),
            ("port", "Port"),
        ],
    )

    def print_report(self):
        data = {
            "ids": self.env.context.get('active_ids', []),
            "model": self.env.context.get('active_model', 'clearance.request'),
            "form": self.read(['transport_type'])[0]
        }
        return self.env.ref("transportation_reports.action_transportation_request_report").report_action(self, data=data)
