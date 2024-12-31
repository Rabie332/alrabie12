odoo.define("clearance_dashboard.transport_dashboard", function (require) {
    "use strict";
    var core = require("web.core");
    var Dashboard = require("dashboard_base.Dashboard");
    var _t = core._t;
    var ajax = require("web.ajax");
    var session = require("web.session");

    var DashboardTransport = Dashboard.extend({
        init: function (parent, context) {
            this._super(parent, context);
            this.date_range = "year";
            this.date_from = moment(new Date(moment().year(), 0, 1));
            this.date_to = moment(new Date(moment().year(), 11, 31));
            this.dashboards_templates = ["transport_dashboard.graphs"];
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
            return self._fetch_data("/clearance_dashboard/fetch_transport_dashboard_data");
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

            // Graph : Vehicles by States

            labels = self.data.vehicles_state_labels;
            datasets = [
                {
                    backgroundColor: window.randomBackgroundColors,
                    data: self.data.vehicles_counts,
                },
            ];
            self.render_graph("#barChartVehiclesStates", "bar", labels, datasets);

            // Graph :  Flow of reward drivers payments by date
            var datasets_payments_drivers = [
                {
                    label: _t("Drivers Rewards"),
                    backgroundColor: window.chartColors.green,
                    borderColor: window.chartColors.green,
                    borderWidth: 1,
                    data: self.data.payment_reward_drivers_data,
                },
            ];
            var options_payments_drivers = {
                responsive: true,
                legend: {
                    display: true,
                    position: "top",
                },
            };
            self.render_graph(
                "#lineDriverReward",
                "line",
                self.data.labels,
                datasets_payments_drivers,
                options_payments_drivers
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

    core.action_registry.add("transport_dashboard", DashboardTransport);
    return DashboardTransport;
});
