odoo.define("hr_deputation_dashboard.dashboard", function (require) {
    "use strict";

    var core = require("web.core");
    var Dashboard = require("hr_dashboard.dashboard");
    var _t = core._t;

    var DashboardHrDeputation = Dashboard.include({
        render_graphs: function () {
            var self = this;
            self._super();
            // Graph : deputations by type
            var datasets = [
                {
                    label: _t("Deputation by types"),
                    backgroundColor: window.randomBackgroundColors,
                    borderWidth: 1,
                    data: self.data.deputations_by_type,
                },
            ];
            var options = {
                responsive: true,
                legend: {
                    display: true,
                    position: "top",
                },
            };
            self.render_graph("#bar_hr_deputation_dashboard", "bar", self.data.types, datasets, options);
        },
    });

    core.action_registry.add("hr_deputation_dashboard", DashboardHrDeputation);
    return DashboardHrDeputation;
});
