odoo.define("hr_dashboard.dashboard", function (require) {
    "use strict";

    var core = require("web.core");
    var Dashboard = require("dashboard_base.Dashboard");

    var DashboardHr = Dashboard.extend({
        init: function (parent, context) {
            this._super(parent, context);
            this.dashboards_templates = ["hr_dashboard.graphs"];
        },

        fetch_data: function () {
            var self = this;
            return self._fetch_data("/hr_dashboard/fetch_dashboard_data");
        },
        render_graphs: function () {
            var self = this;

            // Graph : Employees by department
            var datasets = [
                {
                    backgroundColor: window.randomBackgroundColors,
                    borderWidth: 1,
                    data: self.data.employees_by_department,
                },
            ];
            var option = {
                responsive: true,
                legend: {
                    display: true,
                    position: "top",
                },
            };
            self.render_graph("#pieChartEmployeesByDepartment", "pie", self.data.departments, datasets, option);
            // Graph : Contracts By States
            datasets = [
                {
                    backgroundColor: window.randomBackgroundColors,
                    borderWidth: 1,
                    data: self.data.contracts_by_states,
                },
            ];
            option = {
                responsive: true,
                legend: {
                    display: true,
                    position: "top",
                },
            };
            self.render_graph("#pieChartContractsByStates", "pie", self.data.all_states, datasets, option);
        },
    });

    core.action_registry.add("hr_dashboard", DashboardHr);
    return DashboardHr;
});
