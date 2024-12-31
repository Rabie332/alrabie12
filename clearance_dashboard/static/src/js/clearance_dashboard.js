odoo.define("clearance_dashboard.dashboard", function (require) {
    "use strict";
    var core = require("web.core");
    var Dashboard = require("dashboard_base.Dashboard");
    var _t = core._t;
    var ajax = require("web.ajax");
    var session = require("web.session");

    var DashboardClearance = Dashboard.extend({
        init: function (parent, context) {
            this._super(parent, context);
            this.date_range = "year";
            this.date_from = moment(new Date(moment().year(), 0, 1));
            this.date_to = moment(new Date(moment().year(), 11, 31));
            this.dashboards_templates = ["clearance_dashboard.graphs"];
        },
        willStart: function () {
            var self = this;
            return $.when(ajax.loadLibs(this), this._super())
                .then(function () {
                    return self.fetch_data();
                })
                .then(function () {
                    self.companies = session.user_context.allowed_company_ids;
                    self.date_range = "year";
                });
        },
        _fetch_data: function (route_name) {
            /* Called by fetch_data using the route_name args.*/
            var self = this;
            self.smart_buttons = {};
            self.data = {};
            self.companies = [];
            if (route_name !== false) {
                if (this.date_from_calendar > this.date_to_calendar) {
                    /* eslint-disable no-alert */
                    alert(_t("Date from should be greater than Date to."));
                }
                return this._rpc({
                    route: route_name,
                    params: {
                        date_from:
                            this.date_from.year() +
                            "-" +
                            ("0" + (this.date_from.month() + 1)).slice(-2) +
                            "-" +
                            ("0" + this.date_from.date()).slice(-2),
                        date_to:
                            this.date_to.year() +
                            "-" +
                            ("0" + (this.date_to.month() + 1)).slice(-2) +
                            "-" +
                            ("0" + this.date_to.date()).slice(-2),
                        date_range: this.date_range,
                        date_from_calendar: this.date_from_calendar,
                        date_to_calendar: this.date_to_calendar,
                        companies: session.user_context.allowed_company_ids,
                    },
                }).then(function (result) {
                    self.smart_buttons = result.smart_buttons;
                    self.data = result.data;
                });
            }
        },

        fetch_data: function () {
            var self = this;
            return self._fetch_data("/clearance_dashboard/fetch_clearance_dashboard_data");
        },
        render_graphs: function () {
            var self = this;
            // Graph :Clearances by type

            var labels = [_t("Clearance"), _t("Transport"), _t("Storage"), _t("Other services")];
            var datasets = [
                {
                    backgroundColor: window.randomBackgroundColors,
                    borderWidth: 1,
                    data: self.data.clearance_by_type,
                },
            ];
            var options = {
                responsive: true,
                legend: {
                    display: true,
                    position: "top",
                },
            };
            self.render_graph("#pieChartClearancesTypes", "pie", labels, datasets, options);

            // Graph :Clearance  by States

            labels = [
                _t("Draft"),
                _t("Customs Clearance"),
                _t("Customs Statement"),
                _t("Transport"),
                _t("Receipt and Delivery"),
                _t("Delivery Done"),
                _t("Close deal"),
            ];
            datasets = [
                {
                    backgroundColor: window.randomBackgroundColors,
                    borderWidth: 1,
                    data: self.data.clearance_by_state,
                },
            ];
            options = {
                responsive: true,
                legend: {
                    display: true,
                    position: "top",
                },
            };
            self.render_graph("#pieChartClearanceStates", "doughnut", labels, datasets, options);

            // Graph :  Flow of customer invoices by date
            var datasets_invoices = [
                {
                    label: _t("Customer invoices"),
                    backgroundColor: window.chartColors.red,
                    borderColor: window.chartColors.red,
                    borderWidth: 1,
                    data: self.data.customer_invoice_data,
                },
            ];
            var options_correspondences = {
                responsive: true,
                legend: {
                    display: true,
                    position: "top",
                },
            };
            self.render_graph(
                "#lineCustomerInvoice",
                "line",
                self.data.labels,
                datasets_invoices,
                options_correspondences
            );

            // Graph :  customer invoices by state

            self.render_graph(
                "#barChartInvoiceStates",
                "bar",
                [_t("Draft"), _t("Under Review"), _t("Reviewed"), _t("Confirm"), _t("Validated"), _t("Cancelled")],

                [
                    {
                        backgroundColor: [
                            window.chartColors.purple,
                            window.chartColors.blue,
                            window.chartColors.yellow,
                            window.chartColors.orange,
                            window.chartColors.green,
                            window.chartColors.red,
                        ],
                        borderColor: [
                            window.chartColors.purple,
                            window.chartColors.blue,
                            window.chartColors.yellow,
                            window.chartColors.orange,
                            window.chartColors.green,
                            window.chartColors.red,
                        ],
                        data: [
                            self.data.invoices_draft,
                            self.data.invoices_under_review,
                            self.data.invoices_reviewed,
                            self.data.invoices_confirm,
                            self.data.invoices_posted,
                            self.data.invoices_cancel,
                        ],
                    },
                ]
            );

            // Graph :  Flow of supplier payments by date
            var datasets_payments = [
                {
                    label: _t("Supplier Payments"),
                    backgroundColor: window.chartColors.green,
                    borderColor: window.chartColors.green,
                    borderWidth: 1,
                    data: self.data.supplier_payment_data,
                },
            ];
            var options_payments = {
                responsive: true,
                legend: {
                    display: true,
                    position: "top",
                },
            };
            self.render_graph("#lineSupplierPayment", "line", self.data.labels, datasets_payments, options_payments);

            // Graph :  supplier payments by state

            self.render_graph(
                "#barChartPaymentStates",
                "bar",
                [_t("Draft"), _t("Under Review"), _t("Reviewed"), _t("Confirm"), _t("Validated"), _t("Cancelled")],

                [
                    {
                        backgroundColor: [
                            window.chartColors.purple,
                            window.chartColors.blue,
                            window.chartColors.yellow,
                            window.chartColors.orange,
                            window.chartColors.green,
                            window.chartColors.red,
                        ],
                        borderColor: [
                            window.chartColors.purple,
                            window.chartColors.blue,
                            window.chartColors.yellow,
                            window.chartColors.orange,
                            window.chartColors.green,
                            window.chartColors.red,
                        ],
                        data: [
                            self.data.payments_draft,
                            self.data.payments_under_review,
                            self.data.payments_reviewed,
                            self.data.payments_confirm,
                            self.data.payments_posted,
                            self.data.payments_cancel,
                        ],
                    },
                ]
            );

            // Graph :  Flow of Calendar
            var datasets_calendar = [
                {
                    label: _t("Receipt dates"),
                    backgroundColor: window.chartColors.blue,
                    borderColor: window.chartColors.blue,
                    borderWidth: 1,
                    data: self.data.calendar_data,
                },
            ];
            var options_calendar = {
                responsive: true,
                legend: {
                    display: true,
                    position: "top",
                },
            };
            self.render_graph("#lineClearanceCalendar", "line", self.data.labels, datasets_calendar, options_calendar);

            // Graph : Expenses VS Sales

            labels = [_t("Expenses"), _t("Sales")];
            datasets = [
                {
                    backgroundColor: window.randomBackgroundColors,
                    borderWidth: 1,
                    data: self.data.expense_vs_sales,
                },
            ];
            options = {
                responsive: true,
                legend: {
                    display: true,
                    position: "top",
                },
            };
            self.render_graph("#pieChartSalesExpenses", "pie", labels, datasets, options);

            // Graph : Shipping Orders by Type

            self.render_graph(
                "#barShippingStates",
                "bar",
                [_t("Warehouse"), _t("Customer site"), _t("Other site"), _t("Return empty")],

                [
                    {
                        backgroundColor: [
                            window.chartColors.blue,
                            window.chartColors.yellow,
                            window.chartColors.green,
                            window.chartColors.red,
                        ],
                        borderColor: [
                            window.chartColors.blue,
                            window.chartColors.yellow,
                            window.chartColors.green,
                            window.chartColors.red,
                        ],
                        data: [
                            self.data.shipping_orders_warehouse,
                            self.data.shipping_orders_customer,
                            self.data.shipping_orders_other,
                            self.data.shipping_orders_empty,
                        ],
                    },
                ]
            );
        },
    });

    core.action_registry.add("clearance_dashboard", DashboardClearance);
    return DashboardClearance;
});
