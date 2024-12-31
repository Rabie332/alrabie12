# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class HotelHousekeepingMaintenanceWizard(models.TransientModel):
    _name = "hotel.housekeeping.maintenance.wizard"
    _description = "Hotel Housekeeping Maintenance Wizard"

    date_start = fields.Datetime("Activity Start Date", required=True)
    date_end = fields.Datetime("Activity End Date", required=True)

    def print_report(self):
        data = {
            "ids": self.ids,
            "form": self.read([])[0],
        }
        return self.env.ref(
            "hotel_housekeeping.report_hotel_several_maintenance"
        ).report_action(self, data=data)
