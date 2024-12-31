odoo.define("pos_pay_later.ServicesButton", function (require) {
    "use strict";

    const PosComponent = require("point_of_sale.PosComponent");
    const ProductScreen = require("point_of_sale.ProductScreen");
    const {useListener} = require("web.custom_hooks");
    const Registries = require("point_of_sale.Registries");

    class ServicesButton extends PosComponent {
        constructor() {
            super(...arguments);
            useListener("click", this.onClick);
        }
        async onClick() {
            await this.showTempScreen("ServicesScreen");
        }
    }
    ServicesButton.template = "ServicesButton";

    ProductScreen.addControlButton({
        component: ServicesButton,
        condition: function () {
            return this.env.pos.config.allow_later_payment;
        },
    });

    Registries.Component.add(ServicesButton);

    return ServicesButton;
});
