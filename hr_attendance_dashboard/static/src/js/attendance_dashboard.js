odoo.define("hr_attendance_dashboard.dashboard", function (require) {
    "use strict";

    var core = require("web.core");
    var Dashboard = require("dashboard_base.Dashboard");
    var _t = core._t;
    var ajax = require("web.ajax");

    var DashboardAttendance = Dashboard.extend({
        init: function (parent, context) {
            this._super(parent, context);
            this.date_range = "year";
            this.date_from = moment(new Date(moment().year(), 0, 1));
            this.date_to = moment(new Date(moment().year(), 11, 31));
            this.dashboards_templates = ["hr_attendance_dashboard.graphs"];
        },
        willStart: function () {
            var self = this;
            return $.when(ajax.loadLibs(this), this._super())
                .then(function () {
                    return self.fetch_data();
                })
                .then(function () {
                    self.date_range = "year";
                });
        },
        _fetch_data: function (route_name) {
            /* Called by fetch_data using the route_name args.*/
            var self = this;
            self.smart_buttons = {};
            self.data = {};
            if (route_name !== false) {
                if (this.date_from_calendar > this.date_to_calendar) {
                    alert(_t("Date from should be greater than Date to.")); // eslint-disable-line no-alert
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
                    },
                }).then(function (result) {
                    self.smart_buttons = result.smart_buttons;
                    self.data = result.data;
                });
            }
        },

        fetch_data: function () {
            var self = this;
            return self._fetch_data("/attendance/fetch_dashboard_data");
        },

        render_graphs: function () {
            var self = this;
            // Pie chart vals
            var datasets = [
                {
                    backgroundColor: self.data.graph_data.colors,
                    borderWidth: 1,
                    data: self.data.graph_data.datas,
                },
            ];
            var options = {
                responsive: true,
                legend: {
                    display: true,
                    position: "top",
                },
            };
            self.render_graph("#pieChartAttendance", "pie", self.data.graph_data.labels, datasets, options);

            // Left panel : vals and percentage
            self.$(".all_employees_count").html(self.data.all_employees_count);
            self.$(".onduty").html(self.data.onduty);
            self.$(".absences").html(self.data.absences);
            self.$(".delays").html(self.data.delays);
            self.$(".justified_absences").html(self.data.justified_absences);
            self.$(".public-holidays").html(self.data.public_holidays_count);
            self.$("#onduty_percentage").css("width", self.data.onduty_percentage + "%");
            self.$("#delays_percentage").css("width", self.data.delays_percentage + "%");
            self.$("#absences_percentage").css("width", self.data.absences_percentage + "%");
            self.$("#justified_absences_percentage").css("width", self.data.justified_absences_percentage + "%");
            self.$("#weekend_percentage").css("width", self.data.weekend_percentage + "%");
            // Footer
            self.$("#worked_hours").html(self.data.worked_hours);
            self.$("#real_worked_hours").html(self.data.real_worked_hours);
            self.$("#delay_hours").html(self.data.delay_hours);
            self.$("#overtime_hours").html(self.data.overtime_hours);
            self.$("#authorization_hours").html(self.data.authorization_hours);
            self.$("#authorizations").html(self.data.authorizations);
        },
    });
    core.action_registry.add("hr_attendance_dashboard", DashboardAttendance);
    return DashboardAttendance;
});
