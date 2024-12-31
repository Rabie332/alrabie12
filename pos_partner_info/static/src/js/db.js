odoo.define("pos_partner_info.DB", function (require) {
    "use strict";

    const PosDB = require("point_of_sale.DB");

    PosDB.include({
        _partner_search_string: function (partner) {
            var str = this._super(...arguments);
            if (partner.ref) {
                str += "|" + partner.ref;
                str = str.replace(/\n/g, " ") + "\n";
            }
            return str;
        },
    });

    return PosDB;
});
