from datetime import datetime
import json
from odoo import _, fields, http
from odoo.http import request


class MainController(http.Controller):
    @http.route(
        "/clearance_dashboard/fetch_transport_dashboard_data", type="json", auth="user"
    )
    def fetch_transport_dashboard_data(
        self, date_from, date_to, date_from_calendar, date_to_calendar, companies
    ):
        if date_from_calendar and date_to_calendar:
            date_from = date_from_calendar
            date_to = date_to_calendar
        datetime_from = datetime.strptime(date_from + " 00:00:00", "%Y-%m-%d %H:%M:%S")
        datetime_to = datetime.strptime(date_to + " 23:59:59", "%Y-%m-%d %H:%M:%S")

        clearance_obj = request.env["clearance.request"]
        payment_obj = request.env["account.payment"]
        fleet_obj = request.env["fleet.vehicle"]
        calendar_obj = request.env["calendar.event"]
        shipping_obj = request.env["shipping.order"]

        domain = [
            ("date", ">=", date_from),
            ("date", "<=", date_to),
            ("company_id", "in", companies),
        ]
        domain_calendar = [
            ("start", ">=", datetime_from),
            ("start", "<=", datetime_to),
            ("shipping_order_id", "!=", False),
            ("shipping_order_id.company_id", "in", companies),
        ]
        domain_shipping = [
            ("create_date", ">=", datetime_from),
            ("create_date", "<=", datetime_to),
            ("company_id", "in", companies),
        ]
        domain_payment = [
            ("is_reward_drivers", "=", True),
            ("state", "=", "posted"),
        ] + domain
        clearances = clearance_obj.search(domain)

        packages = clearances.mapped("statement_line_ids").filtered(
            lambda line: line.shipment_type == "fcl"
        )
        packages_number = len(packages)
        shipping_order_customer = (
            request.env["shipping.order"]
            .search(domain_shipping)
            .line_ids.filtered(
                lambda rec: rec.shipping_order_id.transport_type == "customer"
            )
        )
        shipping_order_warehouse = (
            request.env["shipping.order"]
            .search(domain_shipping)
            .line_ids.filtered(
                lambda rec: rec.shipping_order_id.transport_type == "warehouse"
            )
        )
        # calcultate return empty shippping
        shipping_order_empty = (
            request.env["shipping.order"]
            .search(domain_shipping)
            .line_ids.filtered(
                lambda rec: rec.shipping_order_id.transport_type == "empty"
                and rec.goods_id.id
                not in shipping_order_customer.ids + shipping_order_warehouse.ids
            )
        )
        shipping_clearance_port = clearances.filtered(
            lambda clearance: len(clearance.statement_line_ids)
            and (
                len(clearance.statement_line_ids)
                > (
                    clearance.shipping_order_customer
                    + clearance.shipping_order_warehouse
                    + len(shipping_order_empty)
                )
            )
        )
        # flake8: noqa: B950
        shipping_order_warehouse_line_without_customer = [
            shipping_order_line.id
            for shipping_order_line in shipping_order_warehouse
            if shipping_order_line.goods_id
            not in request.env["shipping.order"]
            .search(
                [
                    (
                        "shipping_order_id",
                        "=",
                        shipping_order_line.shipping_order_id.id,
                    ),
                    ("transport_type", "=", "customer"),
                ]
            )
            .mapped("line_ids.goods_id")
            and shipping_order_line.shipping_order_id.clearance_request_id.shipping_order_warehouse
        ]
        payment_reward_drivers = payment_obj.search(domain_payment)
        payment_reward_drivers_count = sum(
            payment_reward_drivers.mapped("amount_total_signed")
        )
        vehicles = fleet_obj.search([("company_id", "in", companies)])
        calendar_event = calendar_obj.search(domain_calendar)
        shipping_orders = shipping_obj.search(domain_shipping)
        shipping_port_count = len(clearances.mapped("statement_line_ids")) - (
            sum(
                clearances.filtered(
                    lambda rec: len(rec.mapped("statement_line_ids"))
                ).mapped("shipping_order_warehouse")
            )
            + sum(
                clearances.filtered(
                    lambda rec: len(rec.mapped("statement_line_ids"))
                ).mapped("shipping_order_customer")
            )
            + len(shipping_order_empty)
        )

        # Graphs
        # Graph: Clearances by type
        request_clearance = len(
            clearances.filtered(lambda clearance: clearance.request_type == "clearance")
        )
        clearances_transport = len(
            clearances.filtered(lambda clearance: clearance.request_type == "transport")
        )
        clearances_storage = len(
            clearances.filtered(lambda clearance: clearance.request_type == "storage")
        )
        request_other = len(
            clearances.filtered(
                lambda clearance: clearance.request_type == "other_service"
            )
        )
        clearance_by_type = [
            request_clearance,
            clearances_transport,
            clearances_storage,
            request_other,
        ]
        # Graph: Clearances by state
        clearance_draft = len(
            clearances.filtered(lambda clearance: clearance.state == "draft")
        )
        clearance_customs_clearance = len(
            clearances.filtered(
                lambda clearance: clearance.state == "customs_clearance"
            )
        )
        clearance_customs_statement = len(
            clearances.filtered(
                lambda clearance: clearance.state == "customs_statement"
            )
        )
        clearance_transport = len(
            clearances.filtered(lambda clearance: clearance.state == "transport")
        )
        clearance_delivery = len(
            clearances.filtered(lambda clearance: clearance.state == "delivery")
        )
        clearance_delivery_done = len(
            clearances.filtered(lambda clearance: clearance.state == "delivery_done")
        )
        clearance_close = len(
            clearances.filtered(lambda clearance: clearance.state == "close")
        )
        clearance_by_state = [
            clearance_draft,
            clearance_customs_clearance,
            clearance_customs_statement,
            clearance_transport,
            clearance_delivery,
            clearance_delivery_done,
            clearance_close,
        ]
        # Flow of customer invoices and supplier payment by date and calendar
        labels = []
        payment_reward_drivers_data = []
        calendar_data = []
        MONTH_NAMES = {
            1: _("January"),
            2: _("February"),
            3: _("March"),
            4: _("April"),
            5: _("May"),
            6: _("June"),
            7: _("July"),
            8: _("August"),
            9: _("September"),
            10: _("October"),
            11: _("November"),
            12: _("December"),
        }
        day_name = {
            0: _("Monday"),
            1: _("Tuesday"),
            2: _("Wednesday"),
            3: _("Thursday"),
            4: _("Friday"),
            5: _("Saturday"),
            6: _("Sunday"),
        }

        week_name = {
            1: _("Week 1"),
            2: _("Week 2"),
            3: _("Week 3"),
            4: _("Week 4"),
            5: " ",
        }
        number_days = (
            datetime.strptime(date_to, "%Y-%m-%d")
            - datetime.strptime(date_from, "%Y-%m-%d")
        ).days + 1
        if number_days <= 1:
            day_number = fields.Date.from_string(date_from).weekday()
            labels.append(day_name[int(day_number)])
            payment_reward_drivers_data.append(payment_reward_drivers_count)

            calendar_data.append(len(calendar_event))

        elif 1 < number_days <= 7:
            for day in range(0, 7):
                labels.append(day_name[day])
                # payment reward drivers
                payments_drivers = payment_reward_drivers.filtered(
                    lambda rec: rec.date and rec.date.weekday() == day
                )
                payment_reward_drivers_data.append(
                    round(sum(payments_drivers.mapped("amount_total_signed")), 2)
                )
                # calendar
                calendar_data.append(
                    len(calendar_event.filtered(lambda rec: rec.start.weekday() == day))
                )
        elif 7 < number_days <= 31:
            for week in range(1, (number_days // 7 + 1) + 1):
                labels.append(week_name[week])
                # payment reward drivers
                payments_drivers = payment_reward_drivers.filtered(
                    lambda rec: rec.date and (rec.date.day) // 7 + 1 == week
                )
                payment_reward_drivers_data.append(
                    round(sum(payments_drivers.mapped("amount_total_signed")), 2)
                )
                # calendar
                calendar_data.append(
                    len(
                        calendar_event.filtered(
                            lambda rec: (rec.start.day) // 7 + 1 == week
                        )
                    )
                )
        elif number_days > 31:
            for month in range(1, 13):
                labels.append(MONTH_NAMES[month])
                # payment reward drivers
                payments_drivers = payment_reward_drivers.filtered(
                    lambda rec: rec.date and rec.date.month == month
                )
                payment_reward_drivers_data.append(
                    round(sum(payments_drivers.mapped("amount_total_signed")), 2)
                )
                # calendar
                calendar_data.append(
                    len(
                        calendar_event.filtered(
                            lambda rec: rec.start.date().month == month
                        )
                    )
                )
        # Graph: Vehicles by State
        vehicles_counts = []
        vehicles_state_labels = []
        vehicle_state = request.env["fleet.vehicle.state"].search([])
        for state in vehicle_state:
            vehicles_state_labels.append(state.name)
            vehicles_counts.append(
                len(vehicles.filtered(lambda rec: rec.state_id.id == state.id))
            )

        # Graph: Shipping Orders by Type

        shipping_orders_warehouse = shipping_orders.filtered(
            lambda rec: rec.transport_type == "warehouse"
        )
        shipping_orders_customer = shipping_orders.filtered(
            lambda rec: rec.transport_type == "customer"
        )
        shipping_orders_other = shipping_orders.filtered(
            lambda rec: rec.transport_type == "other"
        )
        shipping_orders_empty = shipping_orders.filtered(
            lambda rec: rec.transport_type == "empty"
        )

        ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### #####
        #####   CUSTOM CODE
        ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### #####
        domain_custom = [
            # ("date", ">=", date_from),
            # ("date", "<=", date_to),
            ("company_id", "in", companies),
            ("state", "not in", ['canceled','delivery_done',"draft", "close"]),
            ("request_type", "=", "clearance"),
        ]
        clearance_obj_custom = request.env["clearance.request"]
        clearances_custom = clearance_obj_custom.search(domain_custom)
        
        clearance_delivery_warehouse = clearances_custom.filtered(
            lambda clearance_custom:
            clearance_custom.shipping_order_warehouse != 0 and
            any(line.shipment_type == "fcl" for line in clearance_custom.statement_line_ids)
        )
        
        shipping_order_warehouse_total = 0
        for shipping_order in clearance_delivery_warehouse:
            
            shipping_order_warehouse_total += shipping_order.shipping_order_warehouse
        
        clearance_delivery_warehouse_ids = clearance_delivery_warehouse.ids
        custom_action_json = json.dumps({
            "name": "Containers In Yard",
            "res_model": "clearance.request",
            "domain": [("id", "in", clearance_delivery_warehouse_ids)]
        })
        
        domain_custom_port = [
            # ("date", ">=", date_from),
            # ("date", "<=", date_to),
            ("company_id", "in", companies),
            ("state", "not in", ['canceled','delivery_done',"draft"]),
        ]
        
        clearances_custom_port = clearance_obj_custom.search(domain_custom_port)
        
        clearance_delivery_port = clearances_custom_port.filtered(
            lambda clearance_custom:
            clearance_custom.shipping_order_port != 0
        )
        
        
        shipping_order_port_total = 0
        for shipping_order in clearance_delivery_port:
            
            shipping_order_port_total += shipping_order.shipping_order_port

        clearance_delivery_port_ids = clearance_delivery_port.ids
        custom_action_port_json = json.dumps({
            "name": "Containers In Port",
            "res_model": "clearance.request",
            "domain": [("id", "in", clearance_delivery_port_ids)]
        })
        
        
        domain_urgent_requests = [
            # ("date", ">=", date_from),
            # ("date", "<=", date_to),
            ("company_id", "in", companies),
            ("state", "in", ['transport','delivery']),
            ("request_priority", "=", "urgent"),
        ]
        
        clearances_urgent_requests = clearance_obj_custom.search(domain_urgent_requests)
        
        clearances_urgent_requests_ids = clearances_urgent_requests.ids
        action_urgent_request_json = json.dumps({
            "name": "Urgent Requests",
            "res_model": "clearance.request",
            "domain": [("id", "in", clearances_urgent_requests_ids)]
        })
        
        
        ##### ##### ##### ##### ##### ##### ##### ##### ##### ##### #####
        dashboard_data = {
            "data": {
                "clearance_by_type": clearance_by_type,
                "clearance_by_state": clearance_by_state,
                "labels": labels,
                "vehicles_state_labels": vehicles_state_labels,
                "vehicles_counts": vehicles_counts,
                "payment_reward_drivers_data": payment_reward_drivers_data,
                "calendar_data": calendar_data,
                "shipping_orders_warehouse": len(shipping_orders_warehouse),
                "shipping_orders_customer": len(shipping_orders_customer),
                "shipping_orders_other": len(shipping_orders_other),
                "shipping_orders_empty": len(shipping_orders_empty),
            },
            "smart_buttons": [
                {
                    "name": _("Clearances In transportation"),
                    "value": clearance_transport,
                    "no_display": False,
                    "action_name": False,
                    "custom_action": '{"name": "Clearances In transportation'
                    '/المعاملات في النقل",'
                    ' "res_model": "clearance.request", "domain": "[(\'id\', \'in\', %s)])]"}'
                    % clearances.filtered(
                        lambda clearance: clearance.state == "transport"
                    ).ids,
                    "icon": "fa fa-ship",
                    "color_class": "bg-green",
                },
                {
                    "name": _("Clearances Delivery In progress"),
                    "value": clearance_delivery,
                    "no_display": False,
                    "action_name": False,
                    "custom_action": '{"name": "Clearances Delivery In progress'
                    '/المعاملات جاري التوصيل",'
                    ' "res_model": "clearance.request", "domain": "[(\'id\', \'in\', %s)])]"}'
                    % clearances.filtered(
                        lambda clearance: clearance.state == "delivery"
                    ).ids,
                    "icon": "fa fa-money",
                    "color_class": "bg-red",
                },
                {
                    "name": _("Containers In Yard"),
                    "value": shipping_order_warehouse_total,
                    "no_display": False,
                    "action_name": False,
                    "custom_action": custom_action_json,
                    "icon": "fa fa-shopping-cart",
                    "color_class": "bg-yellow",
                },
                {
                    "name": _("Shipments Arrived To Customer"),
                    "value": len(shipping_order_customer.ids),
                    "no_display": False,
                    "action_name": False,
                    "custom_action": '{"name": "Shipments Arrived To Customer'
                    '/شحنات وصلت للعميل",'
                    ' "res_model": "shipping.order.line", "domain": "[(\'id\', \'in\', %s)])]"}'
                    % shipping_order_customer.ids,
                    "icon": "fa fa-truck",
                    "color_class": "bg-blue",
                },
                {
                    "name": _("Containers In Port"),
                    "value": shipping_order_port_total,
                    "no_display": False,
                    "action_name": False,
                    "custom_action": custom_action_port_json,
                    "icon": "fa  fa-credit-card",
                    "color_class": "bg-aqua",
                },
                {
                    "name": _("Packages Number"),
                    "value": packages_number,
                    "no_display": False,
                    "action_name": False,
                    "custom_action": '{"name": "Packages/الحاويات",'
                    ' "res_model": "clearance.request.shipment.type",'
                    " \"domain\": \"[('id', 'in', %s)])]\"}" % packages.ids,
                    "icon": "fa fa-box",
                    "color_class": "bg-blue",
                },
                {
                    "name": _("Urgent Requests"),
                    "value": len(clearances_urgent_requests),
                    "no_display": False,
                    "action_name": False,
                    "custom_action": action_urgent_request_json,
                    "icon": "fa fa-line-chart",
                    "color_class": "bg-dark",
                },
            ],
        }
        return dashboard_data

    @http.route(
        "/clearance_dashboard/fetch_clearance_dashboard_data", type="json", auth="user"
    )
    def fetch_clearance_dashboard_data(
        self, date_from, date_to, date_from_calendar, date_to_calendar, companies
    ):
        if date_from_calendar and date_to_calendar:
            date_from = date_from_calendar
            date_to = date_to_calendar
        datetime_from = datetime.strptime(date_from + " 00:00:00", "%Y-%m-%d %H:%M:%S")
        datetime_to = datetime.strptime(date_to + " 23:59:59", "%Y-%m-%d %H:%M:%S")

        clearance_obj = request.env["clearance.request"]
        payment_obj = request.env["account.payment"]
        move_obj = request.env["account.move"]
        fleet_obj = request.env["fleet.vehicle"]
        calendar_obj = request.env["calendar.event"]
        shipping_obj = request.env["shipping.order"]

        domain = [
            ("date", ">=", date_from),
            ("date", "<=", date_to),
            ("company_id", "in", companies),
        ]
        domain_invoice = [
            ("invoice_date", ">=", date_from),
            ("invoice_date", "<=", date_to),
            ("clearance_request_id", "!=", False),
            ("company_id", "in", companies),
        ]
        domain_calendar = [
            ("start", ">=", datetime_from),
            ("start", "<=", datetime_to),
            ("shipping_order_id", "!=", False),
            ("shipping_order_id.company_id", "in", companies),
        ]
        domain_shipping = [
            ("create_date", ">=", datetime_from),
            ("create_date", "<=", datetime_to),
            ("company_id", "in", companies),
        ]
        domain_payment = [("clearance_request_id", "!=", False)] + domain
        clearances = clearance_obj.search(domain)
        packages = clearances.mapped("statement_line_ids").filtered(
            lambda line: line.shipment_type == "fcl"
        )
        packages_number = len(packages)
        payment_supplier = payment_obj.search(
            [("partner_type", "=", "supplier")] + domain_payment
        )
        payment_supplier_posted = payment_supplier.filtered(
            lambda rec: rec.state == "posted"
        )
        payment_supplier_count = sum(
            payment_supplier_posted.mapped("amount_total_signed")
        )
        invoice_customer = move_obj.search(
            [("move_type", "=", "out_invoice")] + domain_invoice
        )
        invoice_customer_posted = invoice_customer.filtered(
            lambda rec: rec.state == "posted"
        )
        invoice_customer_count = sum(
            invoice_customer_posted.mapped("amount_total_signed")
        )
        fleets = fleet_obj.search([("company_id", "in", companies)])
        # calculate customer balance from paid and partial invoice
        payments_customer = []
        paid_customer_invoices = invoice_customer_posted.filtered(
            lambda rec: rec.payment_state == "paid"
        )
        partial_payments_customer = invoice_customer_posted.filtered(
            lambda rec: rec.payment_state == "partial"
        )
        payment_customer = sum(
            paid_customer_invoices.mapped("amount_total_signed")
        ) + sum(
            invoice.amount_total_signed - invoice.amount_residual_signed
            for invoice in partial_payments_customer
        )
        if payment_customer:
            payments_customer = (
                paid_customer_invoices.ids + partial_payments_customer.ids
            )
        calendar_event = calendar_obj.search(domain_calendar)
        shipping_orders = shipping_obj.search(domain_shipping)

        # Graphs
        # Graph: Clearances by type
        request_clearance = len(
            clearances.filtered(lambda clearance: clearance.request_type == "clearance")
        )
        clearances_transport = len(
            clearances.filtered(lambda clearance: clearance.request_type == "transport")
        )
        clearances_storage = len(
            clearances.filtered(lambda clearance: clearance.request_type == "storage")
        )
        request_other = len(
            clearances.filtered(
                lambda clearance: clearance.request_type == "other_service"
            )
        )
        clearance_by_type = [
            request_clearance,
            clearances_transport,
            clearances_storage,
            request_other,
        ]
        # Graph: Clearances by state
        clearance_draft = len(
            clearances.filtered(lambda clearance: clearance.state == "draft")
        )
        clearance_customs_clearance = len(
            clearances.filtered(
                lambda clearance: clearance.state == "customs_clearance"
            )
        )
        clearance_customs_statement = len(
            clearances.filtered(
                lambda clearance: clearance.state == "customs_statement"
            )
        )
        clearance_transport = len(
            clearances.filtered(lambda clearance: clearance.state == "transport")
        )
        clearance_delivery = len(
            clearances.filtered(lambda clearance: clearance.state == "delivery")
        )
        clearance_delivery_done = len(
            clearances.filtered(lambda clearance: clearance.state == "delivery_done")
        )
        clearance_close = len(
            clearances.filtered(lambda clearance: clearance.state == "close")
        )
        clearance_by_state = [
            clearance_draft,
            clearance_customs_clearance,
            clearance_customs_statement,
            clearance_transport,
            clearance_delivery,
            clearance_delivery_done,
            clearance_close,
        ]
        # Flow of customer invoices and supplier payment by date and calendar
        labels = []
        customer_invoice_data = []
        supplier_payment_data = []
        calendar_data = []
        MONTH_NAMES = {
            1: _("January"),
            2: _("February"),
            3: _("March"),
            4: _("April"),
            5: _("May"),
            6: _("June"),
            7: _("July"),
            8: _("August"),
            9: _("September"),
            10: _("October"),
            11: _("November"),
            12: _("December"),
        }
        day_name = {
            0: _("Monday"),
            1: _("Tuesday"),
            2: _("Wednesday"),
            3: _("Thursday"),
            4: _("Friday"),
            5: _("Saturday"),
            6: _("Sunday"),
        }

        week_name = {
            1: _("Week 1"),
            2: _("Week 2"),
            3: _("Week 3"),
            4: _("Week 4"),
            5: " ",
        }
        number_days = (
            datetime.strptime(date_to, "%Y-%m-%d")
            - datetime.strptime(date_from, "%Y-%m-%d")
        ).days + 1
        if number_days <= 1:
            day_number = fields.Date.from_string(date_from).weekday()
            labels.append(day_name[int(day_number)])
            # Customer Invoices
            customer_invoice_data.append(invoice_customer_count)
            supplier_payment_data.append(payment_supplier_count)

            calendar_data.append(len(calendar_event))

        elif 1 < number_days <= 7:
            for day in range(0, 7):
                labels.append(day_name[day])
                # Customer invoices
                invoices = invoice_customer_posted.filtered(
                    lambda rec: rec.invoice_date and rec.invoice_date.weekday() == day
                )
                customer_invoice_data.append(
                    round(sum(invoices.mapped("amount_total_signed")), 2)
                )
                # payment supplier
                payments = payment_supplier_posted.filtered(
                    lambda rec: rec.date and rec.date.weekday() == day
                )
                supplier_payment_data.append(
                    round(sum(payments.mapped("amount_total_signed")), 2)
                )
                # calendar
                calendar_data.append(
                    len(calendar_event.filtered(lambda rec: rec.start.weekday() == day))
                )
        elif 7 < number_days <= 31:
            for week in range(1, (number_days // 7 + 1) + 1):
                labels.append(week_name[week])
                # Customer invoices
                invoices = invoice_customer_posted.filtered(
                    lambda rec: rec.invoice_date
                    and (rec.invoice_date.day) // 7 + 1 == week
                )
                customer_invoice_data.append(
                    round(sum(invoices.mapped("amount_total_signed")), 2)
                )
                # payment supplier
                payments = payment_supplier_posted.filtered(
                    lambda rec: rec.date and (rec.date.day) // 7 + 1 == week
                )
                supplier_payment_data.append(
                    round(sum(payments.mapped("amount_total_signed")), 2)
                )
                # calendar
                calendar_data.append(
                    len(
                        calendar_event.filtered(
                            lambda rec: (rec.start.day) // 7 + 1 == week
                        )
                    )
                )
        elif number_days > 31:
            for month in range(1, 13):
                labels.append(MONTH_NAMES[month])
                # Customer invoices
                invoices = invoice_customer_posted.filtered(
                    lambda rec: rec.invoice_date and rec.invoice_date.month == month
                )
                customer_invoice_data.append(
                    round(sum(invoices.mapped("amount_total_signed")), 2)
                )
                # payment supplier
                payments = payment_supplier_posted.filtered(
                    lambda rec: rec.date and rec.date.month == month
                )
                supplier_payment_data.append(
                    round(sum(payments.mapped("amount_total_signed")), 2)
                )
                # calendar
                calendar_data.append(
                    len(
                        calendar_event.filtered(
                            lambda rec: rec.start.date().month == month
                        )
                    )
                )
        # Customer invoices by state
        invoices_draft = round(
            sum(
                invoice_customer.filtered(lambda rec: rec.state == "draft").mapped(
                    "amount_total_signed"
                )
            ),
            2,
        )
        invoices_under_review = round(
            sum(
                invoice_customer.filtered(
                    lambda rec: rec.state == "under_review"
                ).mapped("amount_total_signed")
            ),
            2,
        )
        invoices_reviewed = round(
            sum(
                invoice_customer.filtered(lambda rec: rec.state == "reviewed").mapped(
                    "amount_total_signed"
                )
            ),
            2,
        )
        invoices_confirm = round(
            sum(
                invoice_customer.filtered(lambda rec: rec.state == "confirm").mapped(
                    "amount_total_signed"
                )
            ),
            2,
        )

        invoices_cancel = round(
            sum(
                invoice_customer.filtered(lambda rec: rec.state == "cancel").mapped(
                    "amount_total_signed"
                )
            ),
            2,
        )

        # Supplier Payments by state

        payments_draft = round(
            sum(
                payment_supplier.filtered(lambda rec: rec.state == "draft").mapped(
                    "amount_total_signed"
                )
            ),
            2,
        )
        payments_under_review = round(
            sum(
                payment_supplier.filtered(
                    lambda rec: rec.state == "under_review"
                ).mapped("amount_total_signed")
            ),
            2,
        )
        payments_reviewed = round(
            sum(
                payment_supplier.filtered(lambda rec: rec.state == "reviewed").mapped(
                    "amount_total_signed"
                )
            ),
            2,
        )
        payments_confirm = round(
            sum(
                payment_supplier.filtered(lambda rec: rec.state == "confirm").mapped(
                    "amount_total_signed"
                )
            ),
            2,
        )

        payments_cancel = round(
            sum(
                payment_supplier.filtered(lambda rec: rec.state == "cancel").mapped(
                    "amount_total_signed"
                )
            ),
            2,
        )

        # Graph: Expenses VS Sales
        expense_vs_sales = [
            round(payment_supplier_count, 2),
            round(invoice_customer_count, 2),
        ]
        # Graph: Shipping Orders by Type

        shipping_orders_warehouse = shipping_orders.filtered(
            lambda rec: rec.transport_type == "warehouse"
        )
        shipping_orders_customer = shipping_orders.filtered(
            lambda rec: rec.transport_type == "customer"
        )
        shipping_orders_other = shipping_orders.filtered(
            lambda rec: rec.transport_type == "other"
        )
        shipping_orders_empty = shipping_orders.filtered(
            lambda rec: rec.transport_type == "empty"
        )


        ##########################################
        ## Custom Code 
        ##########################################
        
        domain_urgent_requests = [
            # ("date", ">=", date_from),
            # ("date", "<=", date_to),
            ("company_id", "in", companies),
            ("state", "not in", ['canceled','delivery_done',"transport","delivery"]),
            ("clearance_request_priority", "=", "urgent"),
        ]
        
        clearances_urgent_requests = clearance_obj.search(domain_urgent_requests)
        
        clearances_urgent_requests_ids = clearances_urgent_requests.ids
        action_urgent_request_json = json.dumps({
            "name": "Urgent Requests",
            "res_model": "clearance.request",
            "domain": [("id", "in", clearances_urgent_requests_ids)]
        })
        
        ######################################
        ######################################
        dashboard_data = {
            "data": {
                "clearance_by_type": clearance_by_type,
                "clearance_by_state": clearance_by_state,
                "customer_invoice_data": customer_invoice_data,
                "labels": labels,
                "invoices_draft": invoices_draft,
                "invoices_under_review": invoices_under_review,
                "invoices_reviewed": invoices_reviewed,
                "invoices_confirm": invoices_confirm,
                "invoices_posted": self.format_float(invoice_customer_count),
                "invoices_cancel": invoices_cancel,
                "supplier_payment_data": supplier_payment_data,
                "calendar_data": calendar_data,
                "payments_draft": payments_draft,
                "payments_under_review": payments_under_review,
                "payments_reviewed": payments_reviewed,
                "payments_confirm": payments_confirm,
                "payments_posted": self.format_float(payment_supplier_count),
                "payments_cancel": payments_cancel,
                "expense_vs_sales": expense_vs_sales,
                "shipping_orders_warehouse": len(shipping_orders_warehouse),
                "shipping_orders_customer": len(shipping_orders_customer),
                "shipping_orders_other": len(shipping_orders_other),
                "shipping_orders_empty": len(shipping_orders_empty),
            },
            "smart_buttons": [
                {
                    "name": _("Clearances"),
                    "value": len(clearances),
                    "no_display": False,
                    "action_name": False,
                    "custom_action": '{"name": "Clearances/المعاملات",'
                    ' "res_model": "clearance.request", "domain": "[(\'id\', \'in\', %s)])]"}'
                    % clearances.ids,
                    "icon": "fa fa-ship",
                    "color_class": "bg-green",
                },
                {
                    "name": _("Payments"),
                    "value": self.format_float(payment_supplier_count),
                    "no_display": False,
                    "action_name": False,
                    "custom_action": '{"name": "Payments/المدفوعات",'
                    ' "res_model": "account.payment", "domain": "[(\'id\', \'in\', %s)])]"}'
                    % payment_supplier_posted.ids,
                    "icon": "fa fa-money",
                    "color_class": "bg-red",
                },
                {
                    "name": _("Sales"),
                    "value": self.format_float(invoice_customer_count),
                    "no_display": False,
                    "action_name": False,
                    "custom_action": '{"name": "Sales/المبيعات",'
                    ' "res_model": "account.move", "domain": "[(\'id\', \'in\', %s)])]"}'
                    % invoice_customer_posted.ids,
                    "icon": "fa fa-shopping-cart",
                    "color_class": "bg-yellow",
                },
                {
                    "name": _("Fleet"),
                    "value": len(fleets),
                    "no_display": False,
                    "action_name": False,
                    "custom_action": '{"name": "Fleets/المركبات",'
                    ' "res_model": "fleet.vehicle", "domain": "[(\'id\', \'in\', %s)])]"}'
                    % fleets.ids,
                    "icon": "fa fa-truck",
                    "color_class": "bg-blue",
                },
                {
                    "name": _("Customer Balances"),
                    "value": self.format_float(payment_customer),
                    "no_display": False,
                    "action_name": False,
                    "custom_action": '{"name": "Customer Balances/أرصدة العملاء",'
                    ' "res_model": "account.move", "domain": "[(\'id\', \'in\', %s)])]"}'
                    % payments_customer,
                    "icon": "fa  fa-credit-card",
                    "color_class": "bg-aqua",
                },
                {
                    "name": _("Packages Number"),
                    "value": packages_number,
                    "no_display": False,
                    "action_name": False,
                    "custom_action": '{"name": "Packages/الحاويات",'
                    ' "res_model": "clearance.request.shipment.type",'
                    " \"domain\": \"[('id', 'in', %s)])]\"}" % packages.ids,
                    "icon": "fa fa-box",
                    "color_class": "bg-blue",
                },
                {
                    "name": _("Urgent Requests"),
                    "value": len(clearances_urgent_requests),
                    "no_display": False,
                    "action_name": False,
                    "custom_action": action_urgent_request_json,
                    "icon": "fa fa-line-chart",
                    "color_class": "bg-dark",
                },
            ],
        }
        return dashboard_data

    def format_float(self, number):
        """Format float number."""
        is_negative = False
        if number < 0:
            is_negative = True
            number = abs(number)
        number_float = round(number, 2)
        msg = str(number_float).rsplit(".", 2)[0]
        number_float = str(number_float).rsplit(msg, 1)[-1]
        groups = []
        while msg:
            groups.append(msg[-3:])
            msg = msg[:-3]
        if is_negative:
            msg = "-" + msg
        return msg + ",".join(reversed(groups)) + number_float
