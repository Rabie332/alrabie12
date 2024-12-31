/* eslint-disable */
odoo.define("pos_pay_later.PaymentScreen", function (require) {
    "use strict";

    const PaymentScreen = require("point_of_sale.PaymentScreen");
    const Registries = require("point_of_sale.Registries");
    const {notification_utils} = require("pos_notification.notification_utils");

    const CustomPaymentScreen = (PaymentScreen) =>
        class extends PaymentScreen {
            clickPayLater() {
                const self = this;
                const order = self.env.pos.get_order();
                const orderlines = order.get_orderlines();
                const partner_id = order.get_client();
                if (!partner_id) {
                    return notification_utils.showNotification(
                        this,
                        this.env._t(
                            "You cannot perform a later payment. Select a customer first."
                        ),
                        3000
                    );
                } else if (orderlines.length === 0) {
                    return self.showPopup("ErrorPopup", {
                        title: self.env._t("Empty Order"),
                        body: self.env._t(
                            "There must be at least one product in your order."
                        ),
                    });
                }
                this.create_service();
                this.showScreen("ReceiptScreen");
            }
            async create_service() {
                var orders = this.env.pos.db.load("unpaid_orders", []);
                var order = false;
                var order_id = false;
                var pos_order = this.env.pos.get_order();
                if (pos_order) {
                    order_id = pos_order.uid;
                }
                for (var i = 0; i < orders.length; i++) {
                    if (orders[i].id === order_id) {
                        order = orders[i];
                    }
                }
                pos_order.is_service = true;
                return await this.rpc(
                    {
                        model: "pos.service",
                        method: "create_service_from_ui",
                        args: [[order]],
                        kwargs: {context: this.env.pos.pos_session.user_context},
                    },
                    {
                        timeout: 30000,
                        shadow: true,
                    }
                )
                    .then(function () {
                        self.db.remove_order(order.id);
                        self.set("failed", false);
                        return true;
                    })
                    .catch(function (reason) {
                        var error = reason.message;
                        console.warn("Failed to send orders:", order);
                        // Make it as 'not service' in case the cashier wants the make a payment.
                        pos_order.is_service = false;
                        throw error;
                    });
            }
        };

    Registries.Component.extend(PaymentScreen, CustomPaymentScreen);

    return PaymentScreen;
});
