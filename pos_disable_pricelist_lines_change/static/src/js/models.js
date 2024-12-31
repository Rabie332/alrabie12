odoo.define("pos_disable_pricelist_lines_change.models", function (require) {
    "use strict";

    var models = require("point_of_sale.models");
    var _super_order = models.Order.prototype;

    models.Order = models.Order.extend({
        set_pricelist: function (pricelist) {
            if (this.pos.config.disable_pricelist_lines_change) {
                this.pricelist = pricelist;
                this.trigger("change");
            } else {
                _super_order.set_pricelist.apply(this, arguments);
            }
        },
    });

    return models;
});
