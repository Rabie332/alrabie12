odoo.define("clearance.widget_shipping_agent_data", function (require) {
    "use strict";

    var AbstractField = require("web.AbstractField");
    var core = require("web.core");
    var field_registry = require("web.field_registry");
    var QWeb = core.qweb;

    var FieldShippingAgentData = AbstractField.extend({
        init: function () {
            this._super.apply(this, arguments);
        },

        _render: function () {
            return this.$el.html(
                QWeb.render("widget_shipping_agent_data", {
                    shipping_agent_data: this.value,
                })
            );
        },
    });

    field_registry.add("widget_shipping_agent_data", FieldShippingAgentData);

    return FieldShippingAgentData;
});
