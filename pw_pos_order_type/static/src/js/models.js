/* eslint-disable */
odoo.define("pw_pos_order_type.models", function (require) {
    "use strict";
    var models = require("point_of_sale.models");

    models.load_models({
        model: "pos.order.type",
        fields: ["name"],
        domain: function (self) {
            return [["id", "in", self.config.order_type_ids]];
        },
        loaded: function (self, pos_order_type) {
            self.pos_order_type = pos_order_type;
        },
    });
    var _super_Order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function (attributes, options) {
            _super_Order.initialize.apply(this, arguments);
            if (this.pos.config.default_type_id) {
                this.set_order_type(this.pos.config.default_type_id[0]);
            }
        },
        init_from_JSON: function (json) {
            var res = _super_Order.init_from_JSON.apply(this, arguments);
            if (json.order_type_id) {
                this.order_type_id = json.order_type_id;
            }
            return res;
        },
        export_as_JSON: function () {
            var json = _super_Order.export_as_JSON.apply(this, arguments);
            if (this.order_type_id) {
                json.order_type_id = this.order_type_id;
            }
            return json;
        },
        export_for_printing: function () {
            var receipt = _super_Order.export_for_printing.call(this);
            var order_type = this.get_order_type(this.order_type_id);
            receipt.order_type_id = order_type;
            return receipt;
        },
        get_order_type_by_id: function (order_type_id) {
            var self = this;
            var order_type = null;
            for (var i = 0; i < self.pos.pos_order_type.length; i++) {
                if (self.pos.pos_order_type[i].id == order_type_id) {
                    order_type = self.pos.pos_order_type[i];
                }
            }
            return order_type;
        },
        set_order_type: function (order_type_id) {
            this.order_type_id = order_type_id;
            this.trigger("change", this);
        },
        get_order_type: function (order_type_id) {
            return this.get_order_type_by_id(this.order_type_id);
        },
    });
});
