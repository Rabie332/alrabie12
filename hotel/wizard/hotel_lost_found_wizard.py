from odoo import fields, models


class LostFoundReportWizard(models.TransientModel):
    _name = "hotel.lost.found.wizard"
    _description = "Lost Found Report"

    date_from = fields.Datetime("Date from")
    date_to = fields.Datetime("Date to")
    date_type = fields.Selection(
        selection=[
            ("create_date", "Create date"),
            ("delivery_date", "Delivery date"),
            ("found_date", "Found date"),
        ],
        default="found_date",
        string="date",
    )
    type = fields.Selection(
        selection=[("lost", "Lost"), ("found", "Found")], string="Type"
    )

    def print_report(self):
        data = {"ids": [self.id], "form": self.read()[0]}
        return self.env.ref("hotel.report_hotel_lost_found").report_action(
            self, data=data
        )
