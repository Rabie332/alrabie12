/* eslint-disable */
odoo.define("pos_extra_products.ProductsWidget", function (require) {
    "use strict";

    const {useState} = owl.hooks;
    const {useListener} = require("web.custom_hooks");
    const Registries = require("point_of_sale.Registries");
    const ProductsWidget = require("point_of_sale.ProductsWidget");

    const ProductsWidgetNew = (ProductsWidget) =>
        class extends ProductsWidget {
            /**
             * @param {Object} props
             * @param {Number?} props.startCategoryId
             */
            constructor() {
                super(...arguments);
                useListener("update-is-extra", this._updateIsExtra);
                useListener("clear-is-extra", this._clearIsExtra);
                this.state = useState({searchWord: "", isExtra: false});
            }
            get isExtra() {
                // Get is extra
                return this.state.isExtra;
            }
            get productsToDisplay() {
                // Display list products after search by extra product
                var res = super.productsToDisplay;
                if (this.isExtra) {
                    res = this.env.pos.db.search_extra_product_in_category(
                        this.selectedCategoryId,
                        this.isExtra
                    );
                } else {
                    res = super.productsToDisplay.filter(function (product) {
                        return !product.is_extra;
                    });
                }
                return res;
            }
            _tryAddProduct(event) {
                // Don't add extra product automatically in case there only 1 product
                if (event.detail.isExtra) {
                    return;
                }
                return super._tryAddProduct(event);
            }
            _updateIsExtra(event) {
                this.state.isExtra = event.detail;
            }
            _clearIsExtra() {
                // Remove the search after clicking button plus in order line
                this.state.isExtra = false;
            }
            _switchCategory(event) {
                const searchIsExtra = this.env.pos.get("globalSearchIsExtra");
                if (searchIsExtra.el.checked) {
                    searchIsExtra.el.click();
                }
                super._switchCategory(event);
            }
        };
    Registries.Component.extend(ProductsWidget, ProductsWidgetNew);

    return ProductsWidgetNew;
});
