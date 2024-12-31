odoo.define("pos_pay_later.models", function (require) {
    "use strict";

    var models = require("point_of_sale.models");
    var super_order_model = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function () {
            super_order_model.initialize.apply(this, arguments);
            this.is_service = this.is_service || false;
            this.save_to_db();
        },
        export_as_JSON: function () {
            var json = super_order_model.export_as_JSON.apply(this, arguments);
            json.service_id = this.service_id;
            return json;
        },
    });
});
