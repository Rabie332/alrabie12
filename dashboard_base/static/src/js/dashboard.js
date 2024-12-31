/* eslint-disable */
odoo.define("dashboard_base.Dashboard", function (require) {
    "use strict";

    var AbstractAction = require("web.AbstractAction");
    var ajax = require("web.ajax");
    var core = require("web.core");
    var dataset = require("web.data");
    var _t = core._t;
    var QWeb = core.qweb;

    var Dashboard = AbstractAction.extend({
        hasControlPanel: true,
        contentTemplate: "dashboard_base.DashboardMain",

        cssLibs: [
            "/dashboard_base/static/src/css/AdminLTE.css",
            "/dashboard_base/static/src/css/custom.css",
        ],

        jsLibs: [
            "/dashboard_base/static/src/js/libs/Chart.min.js",
            "/dashboard_base/static/src/js/utils.js",
        ],
        events: {
            "click .o_dashboard_action": "on_dashboard_action",
        },

        init: function (parent, context) {
            /*
             * - date_range used to get current filter .possible values :'day', 'week', 'month', year'
             *    ==> By default date_range take day. so date_from = date_to = today.
             * - dashboards_templates used to defines the template will be  rendred for each modules.
             *    ==> dashboards_templates must be defined for each widget inherit from dashboard
             */
            this._super(parent, context);
            this.date_range = "day";
            this.date_from = moment();
            this.date_to = moment();
            this.date_from_calendar = false;
            this.date_to_calendar = false;
            this.dashboards_templates = [];
        },

        willStart: function () {
            var self = this;
            return $.when(ajax.loadLibs(this), this._super()).then(function () {
                return self.fetch_data();
            });
        },

        start: function () {
            /*
             * - Update Control Pane
             * - Render dashboards will be render any templates in  dashboards_templates
             * - Render graphs
             */
            var self = this;
            return this._super().then(function () {
                self.update_cp();
                self.render_dashboards();
                self.render_graphs();
            });
        },

        fetch_data: function () {
            /*
             * Fetch data.Must rewrite this function for any other dashboard to get the right data using controllers.
             *
             * For example to get  list of leads for specific period
             * 1- in your module create a http route like this
             *    @http.route('/crm/fetch_dashboard_data', type='json', auth='user')
             *     def fetch_dashboard_data(self, date_from, date_to):
             *         ...
             *        return data
             * 2-rewrite the fetch_data function in your widget to add the http route name:
             *    fetch_data: function() {
             *       var self = this;
             *       return self._fetch_data('/crm/fetch_dashboard_data');
             *     },
             *
             */
            var self = this;
            return self._fetch_data(false);
        },

        _fetch_data: function (route_name) {
            /* Called by fetch_data using the route_name args.*/
            var self = this;
            self.data = {};
            self.smart_buttons = {};
            self.smart_buttons_info = {};
            if (route_name != false) {
                if (this.date_from_calendar > this.date_to_calendar) {
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
                    },
                }).then(function (result) {
                    self.data = result.data;
                    self.smart_buttons = result.smart_buttons;
                    self.smart_buttons_info = result.smart_buttons_info;
                });
            }
        },

        render_dashboards: function () {
            /*
             * Append any template in dashboards_templates to  the dashboard content.
             *
             */
            var self = this;
            self.$(".dashboard_content").empty();
            _.each(
                ["dashboard_base.smart_buttons"].concat(this.dashboards_templates),
                function (template) {
                    self.$(".dashboard_content").append(
                        QWeb.render(template, {widget: self})
                    );
                }
            );
        },

        render_graphs: function () {
            /*
             * To render graph rewrite this function and implements your code.
             *
             */
            var self = this;
        },

        render_graph: function (
            chartCanvasId,
            chartType,
            chartLabels,
            chartDatasets,
            displayLegend
        ) {
            /*
             * Create Graph using chart.js
             *
             * @param chartCanvasId : the id of canvas
             * @param chartType : chart type (line,bar,pie,doughnut,...)
             * @param chartLabels : See the Legend Label Configuration section below.
             * @param chartDatasets : datasets will be displayed.
             * @param displayLegend : The chart legend displays data about the datasets that are appearing on the chart.
             */
            var self = this;
            var color = Chart.helpers.color;
            var chartData = {
                labels: chartLabels,
                datasets: chartDatasets,
            };
            var ctx = self.$(chartCanvasId).get(0).getContext("2d");
            if (chartType == "bar") {
                new Chart(ctx, {
                    type: "bar",
                    data: chartData,
                    options: {
                        legend: {
                            display: displayLegend,
                            position: "top",
                        },
                        title: {
                            display: false,
                        },
                        tooltips: {
                            mode: "index",
                            intersect: false,
                        },
                        responsive: true,
                        scales: {
                            xAxes: [
                                {
                                    stacked: true,
                                },
                            ],
                            yAxes: [{stacked: true}],
                        },
                    },
                });
            } else {
                new Chart(ctx, {
                    type: chartType,
                    data: chartData,
                    options: {
                        responsive: true,
                        legend: {
                            display: displayLegend,
                            position: "top",
                        },
                    },
                });
            }
        },

        on_dashboard_action: function (event) {
            /*
             * Execute the action defined in  smart buttons 't-att-action_name'
             * the context of the action will content :
             *  - context defined in smart button using 't-att-context'
             *  - search_default_day if date_range is day
             *  - search_default_week if date_range is week
             *  - search_default_month if date_range is month
             *  - search_default_year if date_range is year
             */
            event.preventDefault();
            var $action = $(event.currentTarget);
            if ($action.attr("action_name") != "false") {
                var additional_context = {};
                if (this.date_range === "day") {
                    additional_context = {search_default_day: true};
                } else if (this.date_range === "week") {
                    additional_context = {search_default_week: true};
                } else if (this.date_range === "month") {
                    additional_context = {search_default_month: true};
                } else if (this.date_range === "year") {
                    additional_context = {search_default_year: true};
                }
                var other_context = $action.attr("context");
                additional_context[other_context] = true;
                this.do_action($action.attr("action_name"), {
                    additional_context: additional_context,
                    on_reverse_breadcrumb: function () {
                        parent.history.back();
                    },
                });
            } else if ($action.attr("custom_action") != "false") {
                var custom_action = JSON.parse($action.attr("custom_action"));
                this._do_action(
                    event,
                    custom_action.name,
                    custom_action.res_model,
                    custom_action.domain
                );
            }
        },

        _do_action: function (event, action_name, res_model, domain) {
            /* Note : this function not used
             * Redirect to action using :
             * @param event.
             * @param action_name : Action Name.
             * @param res_model :  the res model
             * @param domain : like  [['type','=','opportunity']] , or [] for empty domain
             */
            var self = this;
            var now = new Date();
            event.preventDefault();
            return this.do_action(
                {
                    name: action_name,
                    type: "ir.actions.act_window",
                    res_model: res_model,
                    view_mode: "tree,form",
                    view_type: "form",
                    views: [
                        [false, "list"],
                        [false, "kanban"],
                        [false, "form"],
                    ],
                    domain: domain,
                    target: "current",
                },
                {
                    on_reverse_breadcrumb: function () {
                        parent.history.back();
                    },
                }
            );
        },

        update_cp: function () {
            /*
             * Update the Control Panel
             */
            var self = this;
            if (!this.$searchview) {
                this.$searchview = $(
                    QWeb.render("dashboard_base.DateRangeButtons", {
                        widget: this,
                    })
                );
                this.$searchview
                    .find("#date_range_" + this.date_range)
                    .addClass("active");
                this.$searchview.click("button.js_date_range", function (ev) {
                    self.on_date_range_button($(ev.target).data("date"));
                    $(this).find("button.js_date_range.active").removeClass("active");
                    $(ev.target).addClass("active");
                });
                this.$searchview
                    .find(".js_date_from")
                    .on("change", self._onChangeDateFrom.bind(this));
                this.$searchview
                    .find(".js_date_to")
                    .on("change", self._onChangeDateTo.bind(this));
            }
            this.updateControlPanel({
                cp_content: {
                    $searchview: this.$searchview,
                },
            });
        },
        _onChangeDateFrom: function (ev) {
            var self = this;
            this.date_from_calendar = $(ev.currentTarget).val();
            $.when(this.fetch_data()).then(function () {
                self.$(".dashboard_content").empty();
                self.render_dashboards();
                self.render_graphs();
            });
        },
        _onChangeDateTo: function (ev) {
            var self = this;
            this.date_to_calendar = $(ev.currentTarget).val();
            $.when(this.fetch_data()).then(function () {
                self.$(".dashboard_content").empty();
                self.render_dashboards();
                self.render_graphs();
            });
        },

        on_date_range_button: function (date_range) {
            /*
             * When date_range changed : fetch_data and render_graphs
             */
            if (date_range === "day") {
                this.date_range = "day";
                this.date_from = moment();
                this.date_to = moment();
                $("#custom_date").addClass("hide");
                $(".js_date_from").val("");
                $(".js_date_to").val("");
                this.date_from_calendar = false;
                this.date_to_calendar = false;
            } else if (date_range === "week") {
                this.date_range = "week";
                this.date_from = moment().startOf("week");
                this.date_to = moment().endOf("week");
                $(".js_date_from").val("");
                $(".js_date_to").val("");
                $("#custom_date").addClass("hide");
                this.date_from_calendar = false;
                this.date_to_calendar = false;
            } else if (date_range === "month") {
                this.date_range = "month";
                this.date_from = moment(new Date(moment().year(), moment().month(), 1));
                this.date_to = moment(
                    new Date(moment().year(), moment().month() + 1, 0)
                );
                $("#custom_date").addClass("hide");
                $(".js_date_from").val("");
                $(".js_date_to").val("");
                this.date_from_calendar = false;
                this.date_to_calendar = false;
            } else if (date_range === "year") {
                this.date_range = "year";
                this.date_from = moment(new Date(moment().year(), 0, 1));
                this.date_to = moment(new Date(moment().year(), 11, 31));
                $("#custom_date").addClass("hide");
                $(".js_date_from").val("");
                $(".js_date_to").val("");
                this.date_from_calendar = false;
                this.date_to_calendar = false;
            } else if (date_range === "custom_date") {
                this.date_range = "custom_date";
                $("#custom_date").removeClass("hide");
            } else {
                console.log(
                    "Unknown date range. Choose between [day, week, month, year]"
                );
                return;
            }
            var self = this;
            $.when(this.fetch_data()).then(function () {
                self.render_dashboards();
                self.render_graphs();
            });
        },
    });

    core.action_registry.add("dashboard_base", Dashboard);

    return Dashboard;
});
