from odoo import fields, models


class PartnerReclamationReportWizard(models.TransientModel):
    _name = "partner.reclamation.wizard"
    _description = "Partner Reclamation Report"

    date_from = fields.Datetime("Date from")
    date_to = fields.Datetime("Date to")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("progress", "In progress"),
            ("solved", "Solved"),
            ("cancel", "Cancelled"),
        ],
        "State",
    )

    def print_report(self):
        data = {"ids": [self.id], "form": self.read()[0]}
        return self.env.ref("hotel_room.report_partner_reclamation").report_action(
            self, data=data
        )
