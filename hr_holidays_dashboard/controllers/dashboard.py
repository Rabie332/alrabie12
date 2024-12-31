import logging

from odoo import _, http
from odoo.http import request

from odoo.addons.hr_dashboard.controllers.dashboard import DashboardController

_logger = logging.getLogger(__name__)


class HolidaysDashboardController(DashboardController):
    @http.route()
    def fetch_hr_dashboard_data(
        self, date_from, date_to, date_range, date_from_calendar, date_to_calendar
    ):
        """Fetch Data."""
        values = super(HolidaysDashboardController, self).fetch_hr_dashboard_data(
            date_from, date_to, date_range, date_from_calendar, date_to_calendar
        )
        url = (
            request.env["ir.config_parameter"]
            .sudo()
            .search([("key", "=", "web.base.url")], limit=1)
            .value
        )

        domain_filter = [
            ("create_date", ">=", date_from),
            ("create_date", "<=", date_to),
        ]
        if date_from_calendar and date_to_calendar:
            domain_filter = [
                ("create_date", ">=", date_from_calendar),
                ("create_date", "<=", date_to_calendar),
            ]
        holiday_domain = [
            "|",
            "&",
            ("date_from", ">=", date_from),
            ("date_from", "<=", date_to),
            "&",
            ("date_to", ">=", date_from),
            ("date_to", "<=", date_to),
        ]
        if date_from_calendar and date_to_calendar:
            holiday_domain = [
                "|",
                "&",
                ("date_from", ">=", date_from_calendar),
                ("date_from", "<=", date_to_calendar),
                "&",
                ("date_to", ">=", date_from_calendar),
                ("date_to", "<=", date_to_calendar),
            ]
        # smart buttons
        employee_in_holidays = (
            request.env["hr.leave"]
            .sudo()
            .search([("state", "not in", ("cancel", "refuse"))] + holiday_domain)
            .mapped("employee_id")
        )
        # Graph :  الاجازات حسب النوع
        holidays_status_obj = request.env["hr.leave.type"]
        all_holidays_type = holidays_status_obj.sudo().search([])
        holidays_type = []
        holidays_by_type = []
        # calculate number for holidays by type
        for holiday_type in all_holidays_type:
            holidays = request.env["hr.leave"].search_count(
                [("holiday_status_id", "=", holiday_type.id)] + domain_filter
            )
            if holidays > 0:
                holidays_type.append(holiday_type.name)
                holidays_by_type.append(holidays)

        data = values.get("data")
        # get requests from data
        requests = values["data"]["requests"]
        top_requests = request.env["hr.leave"].search([] + domain_filter, limit=5)
        for req in top_requests:
            details_url = "{}/web#id={}&view_type=form&model={}".format(
                url, req.id, req._name
            )
            name = _("Holiday request for employee {} with duration {} day(s)").format(
                req.employee_id.name, int(req.number_of_days)
            )
            requests.append(
                {
                    "icon": "fa fa-envelope-open",
                    "name": name,
                    "details_url": details_url,
                }
            )
        data.update(
            {
                "holidays_by_type": holidays_by_type,
                "holidays_type": holidays_type,
                "requests": requests,
            }
        )
        custom_smart_button = {
            "name": _("Employees in holiday"),
            "value": len(employee_in_holidays),
            "no_display": False,
            "action_name": False,
            "custom_action": '{"name": "Employees in holidays / الموظفين في اجازة",'
            ' "res_model":'
            ' "hr.employee", "domain": "[(\'id\', \'in\', %s)])]"}'
            % employee_in_holidays.ids,
            "icon": "fa fa-users",
            "color_class": "bg-success",
        }
        smart_buttons = values.get("smart_buttons")
        smart_buttons.append(custom_smart_button)
        values["smart_buttons"] = smart_buttons
        return values
