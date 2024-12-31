from odoo import fields, models


class EmptyRoomReportWizard(models.TransientModel):
    _name = "empty.room.wizard"
    _description = "Empty Room Wizard"

    days = fields.Integer(string="Days")

    def print_report(self):
        data = {"ids": [self.id], "form": self.read()[0]}
        return self.env.ref("hotel_room.report_empty_room").report_action(
            self, data=data
        )
