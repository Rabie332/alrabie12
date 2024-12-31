/* eslint-disable */
odoo.define("pos_cash_atm.PopUpSelectionBox", function (require) {
    "use strict";

    const {useState} = owl.hooks;
    const AbstractAwaitablePopup = require("point_of_sale.AbstractAwaitablePopup");
    const Registries = require("point_of_sale.Registries");
    const {useListener} = require("web.custom_hooks");
    const PosComponent = require("point_of_sale.PosComponent");
    const {useExternalListener} = owl.hooks;

    class PopUpSelectionBox extends AbstractAwaitablePopup {
        constructor() {
            super(...arguments);
            this._id = 0;
            this.items = this.props.items;
            this.items.forEach(function (i) {
                if (!i.selected) i.selected = false;
            });
            this.state = useState({
                items: this.items,
                onlySelectOne: this.props.onlySelectOne || false,
            });
            useListener("click-item", this.onClickItem);
            useExternalListener(window, "keyup", this._keyUp);
            this.env.pos.lockedUpdateOrderLines = true; // Todo: we locked event keyboard when popup show, when this variable active, ProductScreen trigger method _updateSelectedOrderline wil return
        }

        mounted() {
            super.mounted();
            this.env.pos.lockedUpdateOrderLines = true; // Todo: we locked event keyboard when popup show, when this variable active, ProductScreen trigger method _updateSelectedOrderline wil return
        }

        willUnmount() {
            super.willUnmount();
            const self = this;
            setTimeout(function () {
                self.env.pos.lockedUpdateOrderLines = false; // Timeout 0.5 seconds unlock todo: we locked event keyboard when popup show, when this variable active, ProductScreen trigger method _updateSelectedOrderline wil return
            }, 500);
        }

        async _keyUp(event) {
            if (event.key == "Enter") {
                await this.confirm();
            }
        }

        async onClickItem(event) {
            const item = event.detail.item;
            item.selected = !item.selected;
            this.state.items.forEach(function (i) {
                if (i.id == item.id) {
                    i.selected = item.selected;
                }
            });
            this.state.editModeProps = {
                items: this.state.items,
            };
            if (this.state.onlySelectOne) {
                this.state.items.forEach(function (i) {
                    if (i.id != item.id) {
                        i.selected = false;
                    }
                });
                return await this.confirm();
            }
            this.render();
        }

        get Items() {
            if (!this.state.editModeProps) {
                return this.items;
            }
            return this.state.editModeProps.items;
        }
        get cashier() {
            const pos_cashier = this.env.pos.get_cashier();
            const cashier = this.env.pos.users.find(
                (user) => user.id === pos_cashier.user_id[0]
            );
            return cashier;
        }

        async getPayload() {
            const results = {
                items: this.items.filter((i) => i.selected),
            };
            return results;
        }
    }

    PopUpSelectionBox.template = "PopUpSelectionBox";
    PopUpSelectionBox.defaultProps = {
        confirmText: "Ok",
        cancelText: "Cancel",
        array: [],
        isSingleItem: false,
    };
    Registries.Component.add(PopUpSelectionBox);

    class Item extends PosComponent {
        onKeyup(event) {
            if (event.key === "Enter" && event.target.value.trim() !== "") {
                debugger;
            }
        }
    }

    Item.template = "Item";
    Registries.Component.add(Item);
    return Item;

    return PopUpSelectionBox;
});
