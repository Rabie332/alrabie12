odoo.define("pos_variants_extra_price.models", function (require) {
    "use strict";

    var models = require("point_of_sale.models");

    models.Orderline = models.Orderline.extend({
        generate_wrapped_product_name: function () {
            // 40 * line ratio of .6
            var MAX_LENGTH = 24;
            var wrapped = [];
            // Start patch
            // The next negex will split the full name  by '(', ')' and ',':
            // e.g. 'Cafe (Milk 3$, Honey $5)' -> ['Cafe', 'Milk $3', 'Honey 5$']
            var name_values = this.get_full_product_name().split(/[,()]/);
            var current_line = "";
            for (let name of name_values) {
                while (name.length > 0) {
                    var space_index = name.indexOf(" ");

                    if (space_index === -1) {
                        space_index = name.length;
                    }

                    if (current_line.length + space_index > MAX_LENGTH) {
                        if (current_line.length) {
                            wrapped.push(current_line);
                        }
                        current_line = "";
                    }

                    current_line += name.slice(0, space_index + 1);
                    name = name.slice(space_index + 1);
                }
                if (current_line.length) {
                    wrapped.push(current_line);
                }
                current_line = "";
            }
            //
            return wrapped;
        },
    });
});
