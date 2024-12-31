odoo.define("clearance.widget_customs_declaration_data", function (require) {
    "use strict";

    var AbstractField = require("web.AbstractField");
    var core = require("web.core");
    var field_registry = require("web.field_registry");
    var QWeb = core.qweb;

    var FieldCustomsDeclarationData = AbstractField.extend({
        init: function () {
            this._super.apply(this, arguments);
        },

        _render: function () {
            return this.$el.html(
                QWeb.render("widget_customs_declaration_data", {
                    customs_declaration_data: this.value,
                })
            );
        },
    });

    field_registry.add("widget_customs_declaration_data", FieldCustomsDeclarationData);

    return FieldCustomsDeclarationData;
});
