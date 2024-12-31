import logging
from datetime import date

from odoo import _, http
from odoo.http import request

_logger = logging.getLogger(__name__)


class DashboardController(http.Controller):
    @http.route("/hr_dashboard/fetch_dashboard_data", type="json", auth="user")
    def fetch_hr_dashboard_data(
        self, date_from, date_to, date_range, date_from_calendar, date_to_calendar
    ):
        """Fetch Data."""
        hr_contract_obj = request.env["hr.contract"]
        hr_employee_obj = request.env["hr.employee"]
        # smart buttons
        domain_filter = [
            ("create_date", ">=", date_from),
            ("create_date", "<=", date_to),
        ]
        if date_from_calendar and date_to_calendar:
            domain_filter = [
                ("create_date", ">=", date_from_calendar),
                ("create_date", "<=", date_to_calendar),
            ]
        residence_expiration_employees = hr_employee_obj.search(
            [("residence_end_date", "<", date.today())] + domain_filter
        )
        residence_expiration_employee_count = len(residence_expiration_employees)

        hr_saudi_employee_count = hr_employee_obj.search_count(
            [("country_id.code", "in", ["SA", "sa"])] + domain_filter
        )
        saudi_employees = hr_employee_obj.search(
            [("country_id.code", "in", ["SA", "sa"])] + domain_filter
        )
        non_saudi_employees = hr_employee_obj.search(
            [("country_id.code", "not in", ["SA", "sa"])] + domain_filter
        )
        non_saudi_employee_count = len(non_saudi_employees)
        employees = request.env["hr.employee"].search([])
        present_employees = employees.filtered(
            lambda employee: employee.user_id.im_status == "online"
        )
        absent_employees = employees.filtered(
            lambda employee: employee.user_id.im_status == "offline"
        )

        # last_employee
        last_employees = hr_employee_obj.search(domain_filter, limit=5, order="id desc")
        list_last_employees = []
        if last_employees:
            for employee in last_employees:
                job = ""
                if employee.job_id:
                    job = employee.job_id.name
                list_last_employees.append(
                    {
                        "name": employee.name,
                        "job_name": job,
                        "image_1920": employee.image_1920,
                    }
                )

        # Graph : employees by department
        employees_by_department = []
        departments = []
        all_departments = request.env["hr.department"].search([])
        employees = hr_employee_obj.search([])
        for department in all_departments:
            employee_count = employees.search_count(
                [("department_id", "=", department.id)] + domain_filter
            )
            employees_by_department.append(employee_count)
            departments.append(department.name)

        # Graph : Contracts by state
        contracts_by_states = []
        all_states = ["draft", "open", "close", "cancel"]
        contracts = hr_contract_obj.search([])
        for state in all_states:
            contract_count = contracts.search_count(
                [("state", "=", state)] + domain_filter
            )
            contracts_by_states.append(contract_count)
        # it will be done in deputation and holidays to get the 10 last requests
        last_requests = []
        all_states = [_("New"), _("Running"), _("Expired"), _("Cancelled")]
        return {
            "data": {
                "list_last_employees": list_last_employees,
                "contracts_by_states": contracts_by_states,
                "all_states": all_states,
                "employees_by_department": employees_by_department,
                "departments": departments,
                "requests": last_requests,
            },
            "smart_buttons": [
                {
                    "name": _("Saudi employees"),
                    "value": hr_saudi_employee_count,
                    "no_display": False,
                    "action_name": False,
                    "custom_action": '{"name": "Saudi employees / الموظفين السعوديين", '
                    '"res_model":'
                    ' "hr.employee", "domain": "[(\'id\', \'in\', %s)])]"}'
                    % saudi_employees.ids,
                    "icon": "fa fa-users",
                    "color_class": "bg-green",
                },
                {
                    "name": _("Non Saudi employees"),
                    "value": non_saudi_employee_count,
                    "no_display": False,
                    "action_name": False,
                    "custom_action": '{"name": "Non Saudi employees / الموظفين الغير سعوديين", '
                    '"res_model":'
                    ' "hr.employee", "domain": "[(\'id\', \'in\', %s)])]"}'
                    % non_saudi_employees.ids,
                    "icon": "fa fa-users",
                    "color_class": "bg-aqua",
                },
                {
                    "name": _("Residence expiration employee"),
                    "value": residence_expiration_employee_count,
                    "no_display": False,
                    "action_name": False,
                    "custom_action": "{"
                    '"name": "Residence expiration / الموظفين المنتهيه اقامتهم", '
                    '"res_model":"hr.employee", "domain": "[(\'id\', \'in\', %s)])]"}'
                    % residence_expiration_employees.ids,
                    "icon": "fa fa-users",
                    "color_class": "bg-red",
                },
                {
                    "name": _("Number of connected employees"),
                    "value": len(present_employees),
                    "no_display": False,
                    "action_name": False,
                    "custom_action": '{"name": "عدد الموظفين المداومين / Connected employees", '
                    '"res_model":'
                    ' "hr.employee", "domain": "[(\'id\', \'in\', %s)])]"}'
                    % present_employees.ids,
                    "icon": "fa fa-users",
                    "color_class": "bg-yellow",
                },
                {
                    "name": _("Number of non-connected employees"),
                    "value": len(absent_employees),
                    "no_display": False,
                    "action_name": False,
                    "custom_action": "{"
                    '"name": "Non-connected employees / الموظفين غير المداومين", '
                    '"res_model":"hr.employee", '
                    "\"domain\": \"[('id', 'in', %s)])]\"}" % absent_employees.ids,
                    "icon": "fa fa-users",
                    "color_class": "bg-orange",
                },
            ],
        }
