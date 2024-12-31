from collections import OrderedDict

from odoo import _, http
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.osv import expression

from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager


class CustomerPortal(CustomerPortal):
    def _prepare_quotations_domain(self, partner):
        values = super()._prepare_quotations_domain(partner)
        # related customers of partner can see quotations
        values = expression.OR(
            [
                values,
                [
                    ("partner_id", "in", request.env.user.partner_ids.ids),
                    ("state", "in", ["sent", "cancel"]),
                ],
            ]
        )
        return values

    def _prepare_orders_domain(self, partner):
        values = super()._prepare_orders_domain(partner)
        # related customers of partner can see sale orders
        values = expression.OR(
            [
                values,
                [
                    ("partner_id", "in", request.env.user.partner_ids.ids),
                    ("state", "in", ["sale", "done"]),
                ],
            ]
        )
        return values

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if "clearance_request_count" in counters:
            clearance_request_count = (
                request.env["clearance.request"].search_count(
                    [
                        "|",
                        ("partner_id", "=", request.env.user.partner_id.id),
                        ("partner_id", "in", request.env.user.partner_ids.ids),
                    ]
                )
                if request.env.user.partner_id
                else 0
            )
            values["clearance_request_count"] = clearance_request_count
        if "shipping_order_count" in counters:
            shipping_order_count = (
                request.env["shipping.order"].search_count(
                    [
                        "|",
                        (
                            "clearance_request_id.partner_id",
                            "=",
                            request.env.user.partner_id.id,
                        ),
                        (
                            "clearance_request_id.partner_id",
                            "in",
                            request.env.user.partner_ids.ids,
                        ),
                    ]
                )
                if request.env.user.partner_id
                else 0
            )
            values["shipping_order_count"] = shipping_order_count
        if "shipment_count" in counters:
            shipment_count = (
                request.env["clearance.request.shipment.type"].search_count(
                    [
                        "|",
                        (
                            "clearance_request_id.partner_id",
                            "=",
                            request.env.user.partner_id.id,
                        ),
                        (
                            "clearance_request_id.partner_id",
                            "in",
                            request.env.user.partner_ids.ids,
                        ),
                    ]
                )
                if request.env.user.partner_id
                else 0
            )
            values["shipment_count"] = shipment_count
        return values

    ####################################################################################
    # Clearance Request
    ####################################################################################

    def _get_requests_domain(self):
        return [
            "|",
            ("partner_id", "=", request.env.user.partner_id.id),
            ("partner_id", "in", request.env.user.partner_ids.ids),
        ]

    @http.route(
        ["/my/clearance_requests", "/my/clearance_requests/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_clearance_request(
        self,
        page=1,
        date_begin=None,
        date_end=None,
        sortby=None,
        filterby=None,
        search=None,
        search_in="name",
        **kw
    ):
        values = self._prepare_portal_layout_values()
        ClearanceRequest = request.env["clearance.request"]
        domain = self._get_requests_domain()

        searchbar_sortings = {
            "name": {"label": _("Name"), "order": "name desc"},
            "expected_date_shipment": {
                "label": _("Deadline Shipment"),
                "order": "expected_date_shipment desc",
            },
        }
        # default sort by order
        if not sortby:
            sortby = "expected_date_shipment"
        order = searchbar_sortings[sortby]["order"]
        searchbar_filters = {
            "all": {"label": _("All"), "domain": []},
            "draft": {
                "label": _("Draft"),
                "domain": [("state", "=", "draft")],
            },
            "customs_clearance": {
                "label": _("Customs Clearance"),
                "domain": [("state", "=", "customs_clearance")],
            },
            "transport": {
                "label": _("Transport"),
                "domain": [("state", "=", "transport")],
            },
            "delivery": {
                "label": _("Delivery"),
                "domain": [("state", "=", "delivery")],
            },
            "delivery_done": {
                "label": _("Delivery Done"),
                "domain": [("state", "=", "delivery_done")],
            },
            "close": {
                "label": _("Closed"),
                "domain": [("state", "=", "close")],
            },
        }
        # search by type
        searchbar_inputs = {
            "name": {"input": "name", "label": _("Name")},
            "reference": {"input": "reference", "label": _("Reference")},
            "shipping_number": {
                "input": "shipping_number",
                "label": _("Shipping Number"),
            },
        }

        # default filter by value
        if not filterby:
            filterby = "all"
        domain += searchbar_filters[filterby]["domain"]
        if date_begin and date_end:
            domain += [
                ("create_date", ">", date_begin),
                ("create_date", "<=", date_end),
            ]
        if search and search_in:
            search_domain = []
            if search_in == "name":
                search_domain = [("name", "ilike", search)]
            elif search_in == "reference":
                search_domain = [("reference", "ilike", search)]
            elif search_in == "shipping_number":
                search_domain = [("shipping_number", "ilike", search)]
            domain += search_domain
        # count for pager
        clearance_request_count = ClearanceRequest.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/clearance_requests",
            url_args={
                "date_begin": date_begin,
                "date_end": date_end,
                "sortby": sortby,
                "search_in": search_in,
                "search": search,
            },
            total=clearance_request_count,
            page=page,
            step=self._items_per_page,
        )
        # content according to pager and archive selected
        clearance_requests = ClearanceRequest.search(
            domain, order=order, limit=self._items_per_page, offset=pager["offset"]
        )
        request.session["my_requests_history"] = clearance_requests.ids[:100]

        values.update(
            {
                "date": date_begin,
                "clearance_requests": clearance_requests,
                "page_name": "clearance_request",
                "pager": pager,
                "default_url": "/my/clearance_requests",
                "searchbar_sortings": searchbar_sortings,
                "sortby": sortby,
                "searchbar_filters": OrderedDict(sorted(searchbar_filters.items())),
                "searchbar_inputs": searchbar_inputs,
                "search_in": search_in,
                "search": search,
                "filterby": filterby,
            }
        )
        return request.render("website_farha.portal_my_clearance_requests", values)

    def _clearance_request_get_page_view_values(
        self, clearance_request, access_token, **kwargs
    ):
        values = {
            "page_name": "clearance_request",
            "clearance_request": clearance_request,
        }
        return self._get_page_view_values(
            clearance_request,
            access_token,
            values,
            "my_requests_history",
            False,
            **kwargs
        )

    @http.route(
        ["/my/clearance_requests/<int:clearance_id>"],
        type="http",
        auth="public",
        website=True,
    )
    def portal_my_clearance_request_detail(
        self, clearance_id, access_token=None, report_type=None, download=False, **kw
    ):
        try:
            clearance_sudo = self._document_check_access(
                "clearance.request", clearance_id, access_token
            )
        except (AccessError, MissingError):
            return request.redirect("/my")

        values = self._clearance_request_get_page_view_values(
            clearance_sudo, access_token, **kw
        )
        return request.render("website_farha.portal_clearance_request_page", values)

    def _shipping_order_get_page_view_values(
        self, shipping_order, access_token, **kwargs
    ):
        values = {
            "page_name": "shipping_order",
            "shipping_order": shipping_order,
        }
        return self._get_page_view_values(
            shipping_order,
            access_token,
            values,
            "my_shipping_orders_history",
            False,
            **kwargs
        )

    @http.route(
        ["/my/shipping_orders/<int:shipping_order_id>"],
        type="http",
        auth="public",
        website=True,
    )
    def portal_my_shipping_order_id_detail(
        self,
        shipping_order_id,
        access_token=None,
        report_type=None,
        download=False,
        **kw
    ):
        try:
            shipping_order_sudo = self._document_check_access(
                "shipping.order", shipping_order_id, access_token
            )
        except (AccessError, MissingError):
            return request.redirect("/my")

        values = self._shipping_order_get_page_view_values(
            shipping_order_sudo, access_token, **kw
        )

        return request.render("website_farha.portal_shipping_order_page", values)

    ####################################################################################
    # shipment
    ####################################################################################

    def _get_shipment_domain(self):
        return [
            "|",
            ("clearance_request_id.partner_id", "=", request.env.user.partner_id.id),
            ("clearance_request_id.partner_id", "in", request.env.user.partner_ids.ids),
        ]

    @http.route(
        ["/my/shipments", "/my/shipments/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_shipment(
        self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw
    ):
        values = self._prepare_portal_layout_values()
        Shipment = request.env["clearance.request.shipment.type"]
        domain = self._get_shipment_domain()
        searchbar_sortings = {
            "container_number": {
                "label": _("Container Number"),
                "order": "container_number desc",
            },
            "deadline_shipment_receive": {
                "label": _("Deadline Shipment"),
                "order": "deadline_shipment_receive desc",
            },
        }
        # default sort by order
        if not sortby:
            sortby = "deadline_shipment_receive"
        order = searchbar_sortings[sortby]["order"]
        searchbar_filters = {
            "all": {"label": _("All"), "domain": []},
            "draft": {
                "label": _("Draft"),
                "domain": [("clearance_request_id.state", "=", "draft")],
            },
            "customs_clearance": {
                "label": _("Customs Clearance"),
                "domain": [("clearance_request_id.state", "=", "customs_clearance")],
            },
            "transport": {
                "label": _("Transport"),
                "domain": [("clearance_request_id.state", "=", "transport")],
            },
            "delivery": {
                "label": _("Delivery"),
                "domain": [("clearance_request_id.state", "=", "delivery")],
            },
            "delivery_done": {
                "label": _("Delivery Done"),
                "domain": [("clearance_request_id.state", "=", "delivery_done")],
            },
            "close": {
                "label": _("Closed"),
                "domain": [("clearance_request_id.state", "=", "close")],
            },
            "lcl": {
                "label": _("LCL"),
                "domain": [("shipment_type", "=", "lcl")],
            },
            "fcl": {
                "label": _("FCL"),
                "domain": [("shipment_type", "=", "fcl")],
            },
            "other": {
                "label": _("Other"),
                "domain": [("shipment_type", "=", "other")],
            },
        }

        # default filter by value
        if not filterby:
            filterby = "fcl"
        domain += searchbar_filters[filterby]["domain"]

        if date_begin and date_end:
            domain += [
                ("create_date", ">", date_begin),
                ("create_date", "<=", date_end),
            ]

        # count for pager
        shipment_count = Shipment.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/shipments",
            url_args={"date_begin": date_begin, "date_end": date_end, "sortby": sortby},
            total=shipment_count,
            page=page,
            step=self._items_per_page,
        )
        # content according to pager and archive selected
        shipments = Shipment.search(
            domain, order=order, limit=self._items_per_page, offset=pager["offset"]
        )
        request.session["my_requests_history"] = shipments.ids[:100]

        values.update(
            {
                "date": date_begin,
                "shipments": shipments,
                "page_name": "shipment",
                "pager": pager,
                "default_url": "/my/shipments",
                "searchbar_sortings": searchbar_sortings,
                "sortby": sortby,
                "searchbar_filters": OrderedDict(sorted(searchbar_filters.items())),
                "filterby": filterby,
            }
        )
        return request.render("website_farha.portal_my_shipments", values)
