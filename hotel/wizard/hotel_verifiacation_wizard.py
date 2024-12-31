from odoo import fields, models


class HotelVerificationReportWizard(models.TransientModel):
    _name = "hotel.verification.wizard"
    _description = "Hotel Verification Report"

    date_from = fields.Datetime("Date from")
    date_to = fields.Datetime("Date to")
    type = fields.Selection(
        selection=[
            ("day", "Day"),
            ("night", "Night"),
        ],
        string="Type",
    )

    def print_report(self):
        data = {"ids": [self.id], "form": self.read()[0]}
        return self.env.ref("hotel.report_hotel_verification").report_action(
            self, data=data
        )
