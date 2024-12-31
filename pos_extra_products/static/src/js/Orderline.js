/* eslint-disable */
odoo.define("pos_extra_products.Orderline", function (require) {
    "use strict";

    const OrderLine = require("point_of_sale.Orderline");
    const Registries = require("point_of_sale.Registries");
    const {useState} = owl.hooks;
    const {useListener} = require("web.custom_hooks");

    const OrderLineNew = (OrderLine) =>
        class OrderLineNew extends OrderLine {
            constructor() {
                super(...arguments);
                useListener("click-extra-product", this._ClickExtraProduct);
                useListener("click-product-notes", this._ClickProductNotes);
                this.state = useState({extraBtnClicked: false});
            }
            selectLine() {
                super.selectLine();
                const searchIsExtra = this.env.pos.get("globalSearchIsExtra");
                if (this.state.extraBtnClicked && !searchIsExtra.el.checked) {
                    searchIsExtra.el.click();
                }
                if (!this.state.extraBtnClicked && searchIsExtra.el.checked) {
                    searchIsExtra.el.click();
                }
                this.state.extraBtnClicked = false;
                const order = this.env.pos.get_order();
                const selectedLine = order.get_selected_orderline();
                // Select line product POS category
                this.env.pos.set(
                    "selectedCategoryId",
                    selectedLine.product.pos_categ_id[0]
                );
            }
            async _ClickExtraProduct() {
                const searchIsExtra = this.env.pos.get("globalSearchIsExtra");
                searchIsExtra.el.click();
                this.state.extraBtnClicked = true;
                return true;
            }
            async _ClickProductNotes(event) {
                // Display all product notes
                event.stopPropagation();
                var notes = this.env.pos.notes;
                const order = this.env.pos.get_order();
                const selectedLine = order.get_selected_orderline();
                const {confirmed, payload: inputNote} = await this.showPopup(
                    "ProductNotesPopup",
                    {
                        startingValue: selectedLine.get_note(),
                        title: this.env._t("Product Notes"),
                        notes: notes,
                    }
                );
                if (confirmed) {
                    const order = this.env.pos.get_order();
                    const selectedLine = order.get_selected_orderline();
                    selectedLine.set_note(inputNote);
                }
            }
        };

    Registries.Component.extend(OrderLine, OrderLineNew);

    return OrderLineNew;
});
