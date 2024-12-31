odoo.define("pos_variants_extra_price.ProductConfiguratorPopup", function (require) {
    "use strict";

    const {BaseProductAttribute} = require("point_of_sale.ProductConfiguratorPopup");
    const {patch} = require("web.utils");

    patch(BaseProductAttribute, "pos_variants_extra_price.BaseProductAttribute", {
        getValue() {
            var result = this._super();
            const selected_value = this.values.find(
                (val) => val.id === parseFloat(this.state.selected_value)
            );
            // Start patch
            let value =
                selected_value.name +
                " " +
                this.env.pos.currency.symbol +
                selected_value.price_extra;
            // End patch
            if (selected_value.is_custom && this.state.custom_value) {
                value += `: ${this.state.custom_value}`;
            }
            result.value = value;
            result.extra = selected_value.price_extra;
            return result;
        },
    });
});
