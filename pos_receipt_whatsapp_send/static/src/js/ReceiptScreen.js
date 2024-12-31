/* eslint-disable */
odoo.define("pos_receipt_whatsapp_send.ReceiptScreen", function (require) {
    "use strict";

    const ReceiptScreen = require("point_of_sale.ReceiptScreen");
    const Registries = require("point_of_sale.Registries");
    const {_t} = require("web.core");

    const WhatsappSendReceiptScreen = (ReceiptScreen) =>
        class extends ReceiptScreen {
            sendWhatsapp() {
                // Prepare message
                var pos = this.env.pos;
                var order = pos.get_order();
                var message_welcome = _t("Dear customer");
                var phone = false;
                if (order.get_client()) {
                    message_welcome = _t("Dear ") + order.get_client().name;
                    phone = order.get_client().phone;
                }
                var message =
                    message_welcome +
                    _.str.sprintf(
                        _t(
                            "\nHere is the Order: %s amounting in %s from %s\nFollowing are your order details."
                        ),
                        order.name,
                        pos.format_currency(order.get_total_with_tax()),
                        pos.company.name
                    );
                var details = "";
                order.get_orderlines().forEach(function (line) {
                    details +=
                        "\n\n" +
                        line.product.display_name +
                        _t("\n quantity: ") +
                        line.quantity +
                        _t("\n Price: ") +
                        pos.format_currency(line.price);
                });
                var footer_vals =
                    _t("\n\n\nTotal amount:") +
                    pos.format_currency(order.get_total_with_tax()) +
                    _t("\nChanges: ") +
                    order.get_change() +
                    _t("\nTaxes: ") +
                    order.get_total_tax() +
                    _t("\n\nThank you");

                var RedirectURL =
                    "https://api.whatsapp.com/send?text=" +
                    encodeURIComponent(message) +
                    encodeURIComponent(details) +
                    encodeURIComponent(footer_vals);
                if (phone) {
                    RedirectURL += "&phone=" + phone;
                }
                window.open(RedirectURL, "_blank");
            }
        };
    Registries.Component.extend(ReceiptScreen, WhatsappSendReceiptScreen);
    return ReceiptScreen;
});
