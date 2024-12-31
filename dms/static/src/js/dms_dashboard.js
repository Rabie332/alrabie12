odoo.define("dms_dashboard.dashboard", function (require) {
    "use strict";

    var core = require("web.core");
    var Dashboard = require("dashboard_base.Dashboard");
    var _t = core._t;

    var DashboardDMS = Dashboard.extend({
        init: function (parent, context) {
            this._super(parent, context);
            this.dashboards_templates = ["dms_dashboard.graphs"];
        },

        fetch_data: function () {
            var self = this;
            return self._fetch_data("/dms/fetch_dashboard_data");
        },

        render_graphs: function () {
            var self = this;

            // Graph : Documents by type
            var datasets = [
                {
                    backgroundColor: window.randomBackgroundColors,
                    borderWidth: 1,
                    data: self.data.documents_by_type,
                },
            ];
            var options = {
                responsive: true,
                legend: {
                    display: true,
                    position: "top",
                },
            };
            self.render_graph(
                "#pieChartType",
                "pie",
                self.data.dms_type,
                datasets,
                options
            );

            // Graph : Documents flow
            var flow_datasets = [
                {
                    label: _t("Documents"),
                    backgroundColor: color(window.chartColors.red)
                        .alpha(0.5)
                        .rgbString(),
                    borderColor: window.chartColors.red,
                    borderWidth: 1,
                    data: self.data.document_data,
                },
            ];
            var flow_options = {
                responsive: true,
                legend: {
                    display: true,
                    position: "top",
                },
            };
            self.render_graph(
                "#linedocuments",
                "line",
                self.data.labels,
                flow_datasets,
                flow_options
            );

            // Graph : Folders by tag
            var tag_datasets = [
                {
                    label: _t("Folders by tag"),
                    backgroundColor: window.randomBackgroundColors,
                    borderWidth: 1,
                    data: self.data.folders_by_tag,
                },
            ];
            var tag_options = {
                responsive: true,
                legend: {
                    display: false,
                    position: "top",
                },
            };
            self.render_graph(
                "#barChartTagsFolders",
                "bar",
                self.data.dms_tags,
                tag_datasets,
                tag_options
            );

            // Graph : Documents by extension
            var extension_datasets = [
                {
                    backgroundColor: window.randomBackgroundColors,
                    borderWidth: 1,
                    data: self.data.percent_extension,
                },
            ];
            var extension_options = {
                responsive: true,
                legend: {
                    display: true,
                    position: "top",
                },
            };
            self.render_graph(
                "#doughnutDocuments",
                "doughnut",
                self.data.extensions,
                extension_datasets,
                extension_options
            );

            // Graph : Documents by folder
            var folder_datasets = [
                {
                    label: _t("Documents by folder"),
                    backgroundColor: window.randomBackgroundColors,
                    borderWidth: 1,
                    data: self.data.documents_by_folder,
                },
            ];
            var folder_options = {
                responsive: true,
                legend: {
                    display: false,
                    position: "top",
                },
            };
            self.render_graph(
                "#barChartDocumentsFolders",
                "bar",
                self.data.dms_folder,
                folder_datasets,
                folder_options
            );
        },
    });

    core.action_registry.add("dms_dashboard", DashboardDMS);
    return DashboardDMS;
});
