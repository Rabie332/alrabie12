odoo.define("pos_partner_info.models", function (require) {
    "use strict";

    var models = require("point_of_sale.models");
    models.load_fields("res.partner", ["ref", "is_company"]);
});
