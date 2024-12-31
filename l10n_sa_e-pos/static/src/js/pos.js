odoo.define("l10n_sa_e-pos.PaymentScreen", function (require) {
    'use strict';

    const Registries = require('point_of_sale.Registries');
    const PaymentScreen = require('point_of_sale.PaymentScreen');
    const core = require("web.core");
    const _t = core._t;

    const L10nSaPosPaymentScreen = (PaymentScreen) =>
        class extends PaymentScreen {
            constructor() {
                super(...arguments);
            }
            async _finalizeValidation() {
                if ((this.currentOrder.is_paid_with_cash() || this.currentOrder.get_change()) && this.env.pos.config.iface_cashdrawer) {
                    this.env.pos.proxy.printer.open_cashbox();
                }

                if (!this.currentOrder.get_client()) {
                    this.currentOrder.set_client(this.env.pos.db.get_partner_by_id(this.env.pos.config.default_partner_id[0]));
                }
                this.currentOrder.initialize_validation_date();
                this.currentOrder.finalized = true;

                let syncedOrderBackendIds = [];

                try {
                    if (this.currentOrder.is_to_invoice() || this.env.pos.company.country.code === 'SA') {
                        syncedOrderBackendIds = await this.env.pos.push_and_invoice_order(
                            this.currentOrder
                        );
                    } else {
                        syncedOrderBackendIds = await this.env.pos.push_single_order(this.currentOrder);
                    }
                } catch (error) {
                    if (error.code == 700 || error.code == 701)
                        this.error = true;
                    if (error instanceof Error) {
                        throw error;
                    } else {
                        await this._handlePushOrderError(error);
                    }
                }
                if (syncedOrderBackendIds.length && this.currentOrder.wait_for_push_order()) {
                    const result = await this._postPushOrderResolve(
                        this.currentOrder,
                        syncedOrderBackendIds
                    );
                    if (!result) {
                        await this.showPopup('ErrorPopup', {
                            title: 'Error: no internet connection.',
                            body: error,
                        });
                    }
                }

                this.showScreen(this.nextScreen);

                // If we succeeded in syncing the current order, and
                // there are still other orders that are left unsynced,
                // we ask the user if he is willing to wait and sync them.
                if (syncedOrderBackendIds.length && this.env.pos.db.get_orders().length) {
                    const { confirmed } = await this.showPopup('ConfirmPopup', {
                        title: this.env._t('Remaining unsynced orders'),
                        body: this.env._t(
                            'There are unsynced orders. Do you want to sync these orders?'
                        ),
                    });
                    if (confirmed) {
                        // NOTE: Not yet sure if this should be awaited or not.
                        // If awaited, some operations like changing screen
                        // might not work.
                        this.env.pos.push_orders();
                    }
                }
            }
            async _postPushOrderResolve(order, order_server_ids) {
                try {
                    if (order.is_to_invoice() || order.pos.company.country.code === 'SA') {
                        const result = await this.rpc({
                            model: 'pos.order',
                            method: 'get_qr_code',
                            args: [order_server_ids],
                        }).then(function (qr_code) {
                            return qr_code;
                        });
                        order.set_qr_code(result || null);
                    }
                } finally {
                    return super._postPushOrderResolve(...arguments);
                }
            }
            async _isOrderValid(isForceValidate) {
                var msg = "";
                this.env.pos.get_order().orderlines.each(function (line) {
                    var ldetails = line.get_tax_details();
                    var taxIds = Object.keys(ldetails);
                    // if (taxIds.length === 0) {
                    //     msg += _t("-Each Invoice line shall be categorized with an Invoiced item VAT category code.\n");
                    // }
                });
                if (msg && this.env.pos.company.country.code === "SA") {
                    this.showPopup("ErrorPopup", {
                        title: _t("Validation Error"),
                        body: msg,
                    });
                    return false;
                }
                return super._isOrderValid(isForceValidate);
            }
        };

    Registries.Component.extend(PaymentScreen, L10nSaPosPaymentScreen);

    return PaymentScreen;
});
