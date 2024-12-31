odoo.define("hr_holiday_dashboard.dashboard", function (require) {
    "use strict";

    var core = require("web.core");
    var Dashboard = require("hr_dashboard.dashboard");
    var _t = core._t;

    var DashboardHrHoliday = Dashboard.include({
        render_graphs: function () {
            var self = this;
            self._super();
            // Graph : holidays by type
            var datasets = [
                {
                    label: _t("holidays by types"),
                    backgroundColor: window.randomBackgroundColors,
                    borderWidth: 1,
                    data: self.data.holidays_by_type,
                },
            ];
            var options = {
                responsive: true,
                legend: {
                    display: true,
                    position: "top",
                },
            };
            self.render_graph("#bar_hr_holiday_dashboard", "bar", self.data.holidays_type, datasets, options);
        },
    });

    core.action_registry.add("hr_holiday_dashboard", DashboardHrHoliday);
    return DashboardHrHoliday;
});
