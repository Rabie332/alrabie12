odoo.define("pos_multi_variants.MultipleProductAttribute", function (require) {
    "use strict";

    const {useState} = owl.hooks;
    const Registries = require("point_of_sale.Registries");
    const {
        ProductConfiguratorPopup,
        BaseProductAttribute,
    } = require("point_of_sale.ProductConfiguratorPopup");
    const {patch} = require("web.utils");

    patch(ProductConfiguratorPopup, "pos_multi_variants.ProductConfiguratorPopup", {
        getPayload() {
            var selected_attributes = [];
            var price_extra = 0.0;

            this.env.attribute_components.forEach((attribute_component) => {
                const {value, extra} = attribute_component.getValue();
                // Start patch
                if (value) {
                    selected_attributes.push(value);
                }
                // End patch
                price_extra += extra;
            });

            return {
                selected_attributes,
                price_extra,
            };
        },
    });

    class MultipleProductAttribute extends BaseProductAttribute {
        constructor() {
            super(...arguments);
            this.state = useState({
                selected_value: parseFloat(this.values[0].id),
                selected_values: [],
                custom_value: "",
            });
        }
        _onMultipleClick(ev) {
            const current_value = parseFloat(ev.currentTarget.value);
            if (ev.currentTarget.checked) {
                this.state.selected_values.push(current_value);
            } else {
                const selected_values = this.state.selected_values;
                this.state.selected_values = selected_values.filter(
                    (e) => e !== current_value
                );
            }
        }
        getValue() {
            if (this.state.selected_values) {
                var result = super.getValue();
                const selected_attributes = this.state.selected_values;
                const selected_values = this.values.filter((val) =>
                    selected_attributes.includes(val.id)
                );
                let value = "";
                let price_extra = 0;
                selected_values.forEach((selected_value) => {
                    value +=
                        "+" +
                        selected_value.name +
                        " " +
                        this.env.pos.currency.symbol +
                        selected_value.price_extra;
                    if (selected_value.is_custom && this.state.custom_value) {
                        value += `: ${this.state.custom_value}`;
                    }
                    price_extra += selected_value.price_extra;
                });
                if (value) value = value.substring(1);
                result.value = value;
                result.extra = price_extra;
                return result;
            }
        }
    }
    MultipleProductAttribute.template = "MultipleProductAttribute";
    Registries.Component.add(MultipleProductAttribute);

    return MultipleProductAttribute;
});
