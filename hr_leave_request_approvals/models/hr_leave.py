from collections import defaultdict

from odoo import _, models

from odoo.addons.resource.models.resource import HOURS_PER_DAY


class HrLeave(models.Model):
    _inherit = "hr.leave"

    # ------------------------------------------------------------
    # Business methods
    # ------------------------------------------------------------
    def _prepare_holidays_meeting_values(self):
        """This method is surcharged to Update the meeting values by the right res_id"""
        result = defaultdict(list)
        company_calendar = self.env.company.resource_calendar_id
        for holiday in self:
            calendar = holiday.employee_id.resource_calendar_id or company_calendar
            user = holiday.user_id
            if holiday.leave_type_request_unit == "hour":
                meeting_name = _("%s on Time Off : %.2f hour(s)") % (
                    holiday.employee_id.name or holiday.category_id.name,
                    holiday.number_of_hours_display,
                )
            else:
                meeting_name = _("%s on Time Off : %.2f day(s)") % (
                    holiday.employee_id.name or holiday.category_id.name,
                    holiday.number_of_days,
                )
            meeting_values = {
                "name": meeting_name,
                "duration": holiday.number_of_days
                * (calendar.hours_per_day or HOURS_PER_DAY),
                "description": holiday.notes,
                "user_id": user.id,
                "start": holiday.date_from,
                "stop": holiday.date_to,
                "allday": False,
                "privacy": "confidential",
                "event_tz": user.tz,
                "activity_ids": [(5, 0, 0)],
                "res_id": holiday.id,
            }
            # Add the partner_id (if exist) as an attendee
            if user and user.partner_id:
                meeting_values["partner_ids"] = [(4, user.partner_id.id)]
            result[user.id].append(meeting_values)
        return result
