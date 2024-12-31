odoo.define("pos_cash_atm.pos", function (require) {
    "use strict";

    var models = require("point_of_sale.models");
    models.load_fields("pos.session.history", ["cash", "atm"]);
    models.load_fields("pos.session", ["cash", "atm", "state"]);
});
