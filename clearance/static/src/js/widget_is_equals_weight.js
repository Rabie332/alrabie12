odoo.define("clearance.widget_is_equals_weight", function (require) {
    "use strict";

    var AbstractField = require("web.AbstractField");
    var core = require("web.core");
    var field_registry = require("web.field_registry");
    var QWeb = core.qweb;

    var FieldIsEqualsWeight = AbstractField.extend({
        init: function () {
            this._super.apply(this, arguments);
        },

        _render: function () {
            return this.$el.html(
                QWeb.render("widget_is_equals_weight", {
                    is_equals_weight: this.value,
                })
            );
        },
    });

    field_registry.add("widget_is_equals_weight", FieldIsEqualsWeight);

    return FieldIsEqualsWeight;
});
