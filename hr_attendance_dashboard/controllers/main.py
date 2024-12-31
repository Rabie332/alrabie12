import math

from odoo import _, api, fields, http
from odoo.http import request


def float_time_convert_str(float_val):
    """Convert time format to float value.

    :return: string HH:MM
    """
    factor = float_val < 0 and -1 or 1
    val = abs(float_val)
    hour = factor * int(math.floor(val))
    minute = int((val % 1) * 60)
    return "%s:%s" % (str(hour).zfill(2), str(minute).zfill(2))


class AttendenceDashboard(http.Controller):
    @http.route("/attendance/fetch_dashboard_data", type="json", auth="user")
    def fetch_dashboard_data(
        self, date_from, date_to, date_from_calendar, date_to_calendar
    ):
        "Fetch attendances dashboard data"
        domain_filter = [("date", ">=", date_from), ("date", "<=", date_to)]
        if date_from_calendar and date_to_calendar:
            domain_filter = [
                ("date", ">=", date_from_calendar),
                ("date", "<=", date_to_calendar),
            ]
        summary_line_obj = request.env["hr.attendance.summary.line"].sudo()
        fields.Date.today()
        all_employees_count = request.env["hr.employee"].sudo().search_count([])
        authorizations = (
            request.env["hr.authorization"]
            .sudo()
            .search([("duration", ">", 0.0), ("state", "=", "done")] + domain_filter)
        )
        delays = summary_line_obj.search([("delay_hours", ">", 0.0)] + domain_filter)
        onduty = summary_line_obj.search(
            [("presence_state", "=", "service")] + domain_filter
        )
        absences = summary_line_obj.search(
            [("presence_state", "=", "absent")] + domain_filter
        )

        justified_absences = summary_line_obj.search(
            [("presence_state", "not in", ["service", "absent"])] + domain_filter
        )
        all_attendance_lines = summary_line_obj.sudo().search([])
        overtime_hours = sum(all_attendance_lines.mapped("overtime_hours"))

        # Calculate public holidays
        hr_public_holiday_obj = request.env["hr.public.holiday"]
        public_holidays_count = hr_public_holiday_obj.search_count(
            [
                ("state", "=", "done"),
                ("date_from", ">=", date_from),
                ("date_to", "<=", date_to),
            ]
        )

        # Calculate worked hours
        worked_hours = sum(all_attendance_lines.mapped("worked_hours"))

        # Calculate authorization hours
        authorization_hours = sum(authorizations.mapped("duration"))
        # Calculate delay hours
        delay_hours = sum(delays.mapped("delay_hours"))
        # dashboard data
        graph_data = self.attendance_chart(date_from, date_to)

        return {
            "data": {
                "graph_data": graph_data,
                "public_holidays_count": public_holidays_count,
                "onduty_percentage": format(
                    len(onduty) * 100 / (all_employees_count or 1.0), ".2f"
                ),
                "absences_percentage": format(
                    len(absences) * 100 / (all_employees_count or 1.0), ".2f"
                ),
                "delays_percentage": format(
                    len(delays) * 100 / (all_employees_count or 1.0), ".2f"
                ),
                "absence_justified_percentage": format(
                    len(justified_absences) * 100 / (all_employees_count or 1.0),
                    ".2f",
                ),
                "worked_hours": float_time_convert_str(worked_hours),
                "real_worked_hours": float_time_convert_str(worked_hours - delay_hours),
                "overtime_hours": float_time_convert_str(overtime_hours),
                "delay_hours": float_time_convert_str(delay_hours),
                "authorization_hours": float_time_convert_str(authorization_hours),
                "authorizations": len(authorizations),
                "all_employees_count": all_employees_count,
                "onduty": len(onduty),
                "delays": len(delays),
                "absences": len(absences),
                "justified_absences": len(justified_absences),
            },
            "smart_buttons": [
                {
                    "name": _("Employees"),
                    "value": all_employees_count,
                    "action_name": "hr.open_view_employee_list_my",
                    "icon": "fa fa-users",
                    "color_class": "bg-aqua",
                },
                {
                    "name": _("On duty"),
                    "value": len(onduty),
                    "action_name": False,
                    "custom_action": '{"name": "On duty / الحضور", "res_model": "'
                    'hr.attendance.summary.line", "domain": "[(\'id\', \'in\', %s)])]"}'
                    % onduty.ids,
                    "icon": "fa fa-user-plus",
                    "color_class": "bg-green",
                },
                {
                    "name": _("Delays"),
                    "value": len(delays),
                    "action_name": False,
                    "custom_action": '{"name": "Delays / تأخير", '
                    '"res_model": "hr.attendance.summary.line", '
                    "\"domain\": \"[('id', 'in', %s)])]\"}" % delays.ids,
                    "icon": "fa fa-hourglass-2",
                    "color_class": "bg-yellow",
                },
                {
                    "name": _("Authorizations"),
                    "value": len(authorizations),
                    "action_name": False,
                    "custom_action": '{"name": "Authorizations / استئذانات",'
                    ' "res_model": "hr.authorization", "domain": "[(\'id\', \'in\', %s)])]"}'
                    % authorizations.ids,
                    "context": "search_default_filter_authorizations",
                    "icon": "fa fa-clock-o",
                    "color_class": "bg-orange",
                },
                {
                    "name": _("Absences"),
                    "value": len(absences),
                    "action_name": False,
                    "custom_action": '{"name": "Absences / الغيابات", '
                    '"res_model": "hr.attendance.summary.line",'
                    " \"domain\": \"[('id', 'in', %s)])]\"}" % absences.ids,
                    "icon": "fa fa-calendar-times-o",
                    "color_class": "bg-red",
                },
                {
                    "name": _("Justified Absences"),
                    "value": len(justified_absences),
                    "action_name": False,
                    "custom_action": '{"name": "Justified Absences / غياب مبرر", '
                    '"res_model": "hr.attendance.summary.line", '
                    "\"domain\": \"[('id', 'in', %s)])]\"}" % justified_absences.ids,
                    "icon": "fa fa-calendar-check-o",
                    "color_class": "bg-forestgreen",
                },
            ],
        }

    @api.model
    def attendance_chart(self, date_from, date_to):
        """Get attendances chart info."""
        summary_line_obj = request.env["hr.attendance.summary.line"].sudo()
        domain_filter = [("date", ">=", date_from), ("date", "<=", date_to)]
        labels = [
            _("On duty"),
            _("Absences"),
            _("Justified absences"),
            _("Public holidays"),
        ]
        datas = []
        colors = []
        fields.Date.today()
        request.env["hr.employee"].sudo().search_count([])
        colors.append("#00a65a")
        # onduty
        onduty = summary_line_obj.search(
            [("presence_state", "=", "service")] + domain_filter
        )
        datas.append(len(onduty))
        colors.append("#f56954")
        # absences
        absences = summary_line_obj.search(
            [("presence_state", "=", "absent")] + domain_filter
        )
        datas.append(len(absences))
        colors.append("#25cc25")
        # justified_absences
        justified_absences = summary_line_obj.search(
            [("presence_state", "not in", ["service", "absent"])] + domain_filter
        )
        datas.append(len(justified_absences))
        return {"labels": labels, "datas": datas, "colors": colors}
