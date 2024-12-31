odoo.define("pos_pay_later.ServiceDetails", function (require) {
    "use strict";

    const AbstractAwaitablePopup = require("point_of_sale.AbstractAwaitablePopup");
    const Registries = require("point_of_sale.Registries");
    const models = require("point_of_sale.models");
    const { notification_utils } = require("pos_notification.notification_utils");
    const rpc = require('web.rpc');

    class ServiceDetails extends AbstractAwaitablePopup {
        checkout_service() {
            this.trigger("close-popup");
            this.trigger("close-temp-screen");
            var order = new models.Order({}, {pos: this.env.pos});
            var self = this;
            // Set client
            var client = this.env.pos.db.get_partner_by_id(
                self.props.service.partner_id[0]
            );
            order.set_client(client);

            var service_lines = this.props.ServiceLines;
            service_lines.forEach(function (line) {
                var product = self.env.pos.db.get_product_by_id(line.product_id[0]);
                order.add_product(product, {
                    discount: line.discount,
                    quantity: line.qty,
                    price: line.price_unit,
                });
            });
            const service = this.props.service;
            order.service_id = service.id;
            order.set_screen_data({name: "PaymentScreen"});
            if (order.saveChanges) {
                order.saveChanges();
            }
            this.env.pos.get("orders").add(order);
            this.env.pos.set("selectedOrder", order);
            // Show product screen if taxes were changed or if there's any unknown
            // error that affected the total.
            if (service && service.amount_total !== order.get_total_with_tax()) {
                notification_utils.showNotification(
                    this,
                    this.env._t(
                        "Total is different, please check if there are taxes differences."
                    ),
                    6000
                );
                this.showScreen("ProductScreen");
            }
        }

        moveToStateDone() {
            const self = this;
            rpc.query({
                model: 'pos.service',
                method: 'set_service_state_done',
                args: [[this.props.service.id]],
            }).then(function () {
                self.showPopup('ConfirmPopup', {
                    title: self.env._t('Success'),
                    body: self.env._t('The service state has been set to Done.'),
                });
                // Consider refreshing the service list or updating the UI accordingly
            }).catch(function (err) {
                console.error('Failed to update service state', err);
                self.showPopup('ErrorPopup', {
                    title: self.env._t('Error'),
                    body: self.env._t('Failed to update the service state. Please try again.'),
                });
            });
        }
    }

    ServiceDetails.template = "ServiceDetails";
    Registries.Component.add(ServiceDetails);
    return ServiceDetails;
});
