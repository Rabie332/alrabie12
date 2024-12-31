/* eslint-disable */
odoo.define("pos_extra_products.ProductsWidgetControlPanel", function (require) {
    "use strict";

    const {useRef} = owl.hooks;
    const {debounce} = owl.utils;
    const Registries = require("point_of_sale.Registries");
    const ProductsWidgetControlPanel = require("point_of_sale.ProductsWidgetControlPanel");
    const ProductsWidgetControlPanelNew = (ProductsWidgetControlPanel) =>
        class extends ProductsWidgetControlPanel {
            constructor() {
                super(...arguments);
                this.searchIsExtra = useRef("update-is-extra");
                this.updateIsExtra = debounce(this.updateIsExtra, 100);
                this.env.pos.set("globalSearchIsExtra", useRef("update-is-extra"));
            }
            clearIsExtra() {
                // Remove text from references input and trigger method to remove list of products display after search by references
                this.searchIsExtra.el.value = false;
                this.trigger("clear-is-extra");
            }
            updateIsExtra(event) {
                // Display list of products after search by references (typing 3 character min)
                this.trigger("update-is-extra", event.target.checked);
                if (event.target.checked) {
                    // We are passing the searchWordInput ref so that when necessary,
                    // it can be modified by the parent.
                    this.trigger("try-add-product", {isExtra: event.target.checked});
                } else {
                    this.trigger("clear-is-extra");
                }
            }
        };

    Registries.Component.extend(
        ProductsWidgetControlPanel,
        ProductsWidgetControlPanelNew
    );

    return ProductsWidgetControlPanelNew;
});
