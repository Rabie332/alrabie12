odoo.define("pw_pos_order_type.OrderTypeButton", function (require) {
    "use strict";

    const PosComponent = require("point_of_sale.PosComponent");
    const ProductScreen = require("point_of_sale.ProductScreen");
    const {useListener} = require("web.custom_hooks");
    const Registries = require("point_of_sale.Registries");

    class OrderTypeButton extends PosComponent {
        constructor() {
            super(...arguments);
            useListener("click", this.onClick);
        }
        get order_type() {
            var order = this.env.pos.get_order();
            return order.get_order_type();
        }
        async onClick() {
            const selectionList = this.env.pos.pos_order_type.map((order_type) => ({
                id: order_type.id,
                label: order_type.name,
                item: order_type,
            }));

            const {confirmed, payload: selectedType} = await this.showPopup(
                "SelectionPopup",
                {
                    title: this.env._t("Select Order Type"),
                    list: selectionList,
                }
            );

            if (!confirmed) return false;

            if (confirmed) {
                var order = this.env.pos.get_order();
                order.set_order_type(selectedType.id);
            }
        }
    }
    OrderTypeButton.template = "OrderTypeButton";
    ProductScreen.addControlButton({
        component: OrderTypeButton,
        condition: function () {
            return this.env.pos.config.enable_order_type;
        },
    });
    Registries.Component.add(OrderTypeButton);
    return OrderTypeButton;
});
