odoo.define("clearance.widget_is_not_customs_data", function (require) {
    "use strict";

    var AbstractField = require("web.AbstractField");
    var core = require("web.core");
    var field_registry = require("web.field_registry");
    var QWeb = core.qweb;

    var FieldIsNotCustomsData = AbstractField.extend({
        init: function () {
            this._super.apply(this, arguments);
        },

        _render: function () {
            return this.$el.html(
                QWeb.render("widget_is_not_customs_data", {
                    is_not_customs_data: this.value,
                })
            );
        },
    });

    field_registry.add("widget_is_not_customs_data", FieldIsNotCustomsData);

    return FieldIsNotCustomsData;
});
