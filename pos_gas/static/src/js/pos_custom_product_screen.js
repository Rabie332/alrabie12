odoo.define("pos_gas.ProductScreen", function (require) {
    "use strict";

    const ProductScreen = require("point_of_sale.ProductScreen");
    const Registries = require("point_of_sale.Registries");

    const gasStationDict = {
        "Fuel 95 -- بنزين 95": 2.33,
        "Fuel 91 -- بنزين 91": 2.18,
        "Diesel -- ديزل": 1.15,
    };

    const PosCustomProductScreen = (ProductScreen) =>
        class extends ProductScreen {
            async _clickProduct(event) {
                console.log("Product clicked", event.detail);
                await super._clickProduct(event);

                const product = event.detail;
                console.log("Product name from event:", product.display_name);
                // Check if the product is a fuel product and the POS is configured as a gas station
                if (
                    gasStationDict[product.display_name] &&
                    this.env.pos.config.is_gas_station
                ) {
                    this.state.numpadMode = "price";
                    this.trigger("set-numpad-mode", {mode: "price"});
                    console.log("Numpad mode set to price for", product.display_name);
                }
            }
            async _updateSelectedOrderline(event) {
                await super._updateSelectedOrderline(event);

                let selectedLine = this.currentOrder.get_selected_orderline();
                if (
                    selectedLine &&
                    gasStationDict[selectedLine.product.display_name] &&
                    this.state.numpadMode === "price" &&
                    this.env.pos.config.is_gas_station
                ) {
                    const totalPrice = parseFloat(event.detail.buffer);
                    if (!isNaN(totalPrice)) {
                        const pricePerLiter =
                            gasStationDict[selectedLine.product.display_name];
                        const quantity = totalPrice / pricePerLiter; // Calculate quantity based on the specific fuel price

                        selectedLine.set_quantity(quantity);
                        selectedLine.set_unit_price(pricePerLiter); // Set unit price based on the specific fuel
                        this.currentOrder
                            .get_selected_orderline()
                            .trigger("change", this.currentOrder);
                    }
                }
            }
        };

    Registries.Component.extend(ProductScreen, PosCustomProductScreen);
});
