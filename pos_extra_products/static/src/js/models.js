/* eslint-disable */
odoo.define("pos_extra_products.notes", function (require) {
    "use strict";

    var models = require("point_of_sale.models");

    models.load_models([
        {
            model: "pos.notes",
            fields: ["name", "id"],
            loaded: function (self, notes) {
                self.notes = notes;
                self.note_by_id = {};
                self.notes.forEach(function (note) {
                    self.note_by_id[note.id] = note;
                });
            },
        },
    ]);

    var posmodel_super = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        load_server_data: function () {
            var self = this;
            return posmodel_super.load_server_data
                .apply(this, arguments)
                .then(function () {
                    var note_ids = _.map(self.notes, function (note) {
                        return note.id;
                    });
                });
        },
    });

    models.load_fields("product.product", ["is_extra"]);

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        add_product: function (product, options) {
            if (product.is_extra) {
                this.assert_editable();
                options = options || {};
                var line = new models.Orderline(
                    {},
                    {pos: this.pos, order: this, product: product}
                );
                const selectedLine = this.get_selected_orderline();
                var index = this.orderlines.indexOf(selectedLine);
                this.orderlines.add(line, {at: index + 1});
            } else {
                _super_order.add_product.apply(this, arguments);
            }
        },
    });
    var OrderlineSuper = models.Orderline;
    models.Orderline = models.Orderline.extend({
        export_for_printing: function () {
            var line = OrderlineSuper.prototype.export_for_printing.call(this);
            line.is_extra = this.get_product().is_extra;
            return line;
        },
    });
});
