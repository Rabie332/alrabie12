odoo.define("pos_products_exclude.models", function (require) {
    "use strict";
    var models = require("point_of_sale.models");
    models.PosModel.prototype.models.some(function (model) {
        if (model.model !== "product.product") {
            return false;
        }
        var url = new URL(window.location.href);
        model.domain = [
            ["unavailable_pos_ids", "not in", [url.searchParams.get("config_id")]],
        ];
        // Exit early the iteration of this.models
        return true;
    });
});
