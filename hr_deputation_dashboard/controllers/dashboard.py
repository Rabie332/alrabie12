import logging

from odoo import _, http
from odoo.http import request

from odoo.addons.hr_dashboard.controllers.dashboard import DashboardController

_logger = logging.getLogger(__name__)


class DeputationDashboardController(DashboardController):
    @http.route()
    def fetch_hr_dashboard_data(
        self, date_from, date_to, date_range, date_from_calendar, date_to_calendar
    ):
        """Fetch Data."""
        values = super(DeputationDashboardController, self).fetch_hr_dashboard_data(
            date_from, date_to, date_range, date_from_calendar, date_to_calendar
        )
        url = (
            request.env["ir.config_parameter"]
            .sudo()
            .search([("key", "=", "web.base.url")], limit=1)
            .value
        )

        if date_from_calendar and date_to_calendar:
            date_from = date_from_calendar
            date_to = date_to_calendar
        deputation_domain = [
            "|",
            "&",
            ("date_from", ">=", date_from),
            ("date_from", "<=", date_to),
            "&",
            ("date_to", ">=", date_from),
            ("date_to", "<=", date_to),
        ]
        if date_from_calendar and date_to_calendar:
            deputation_domain = [
                "|",
                "&",
                ("date_from", ">=", date_from_calendar),
                ("date_from", "<=", date_to_calendar),
                "&",
                ("date_to", ">=", date_from_calendar),
                ("date_to", "<=", date_to_calendar),
            ]
        # get the 5 last requests
        top_requests = (
            request.env["hr.deputation"].sudo().search([] + deputation_domain, limit=5)
        )
        requests = values["data"]["requests"]
        data = values["data"]
        for req in top_requests:
            name = _("Deputation request number {} for employee {}").format(
                req.name, req.employee_id.name
            )
            details_url = "{}/web#id={}&view_type=form&model={}".format(
                url, req.id, req._name
            )
            requests.append(
                {"icon": "fa fa-briefcase", "name": name, "details_url": details_url}
            )

        # Graph : deputations by types
        deputations_by_type = []
        types = []
        all_types = request.env["request.type"].search(
            [("res_model", "=", "hr.deputation")]
        )

        deputations = request.env["hr.deputation"].search([])
        for deputation_type in all_types:
            deputations_count = deputations.search_count(
                [("request_type_id", "=", deputation_type.id)] + deputation_domain
            )
            deputations_by_type.append(deputations_count)
            types.append(deputation_type.name)
        data = values["data"]
        data.update(
            {
                "types": types,
                "deputations_by_type": deputations_by_type,
                "requests": requests,
            }
        )
        return values
