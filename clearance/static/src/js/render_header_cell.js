odoo.define("clearance", function (require) {
    "use strict";

    // Remove string for field when it have widgets widget shipping agent data or widget customs declaration data or widget is not good data or widget is equals weight or widget is not customs data
    var ListRenderer = require("web.ListRenderer");
    ListRenderer.include({
        _renderHeaderCell: function (node) {
            var $td = this._super.apply(this, arguments);
            var name = node.attrs.name;
            var widget = node.attrs.widget;
            var field = this.state.fields[name];
            if (
                (field !== undefined && widget === "widget_shipping_agent_data") ||
                widget === "widget_customs_declaration_data" ||
                widget === "widget_is_not_goods_data" ||
                widget === "widget_is_equals_weight" ||
                widget === "widget_is_not_customs_data"
            ) {
                $td.text("");
                $td.css({width: "1%"});
            }
            return $td;
        },
    });
});
