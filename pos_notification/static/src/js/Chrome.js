/* eslint-disable */
odoo.define("pos_notification.chrome", function (require) {
    "use strict";

    const Chrome = require("point_of_sale.Chrome");
    const Registries = require("point_of_sale.Registries");
    const {useListener} = require("web.custom_hooks");
    const {useState} = owl;

    const NotificationChrome = (Chrome) =>
        class extends Chrome {
            constructor() {
                super(...arguments);
                useListener("show-notification", this._onShowNotification);
                useListener("close-notification", this._onCloseNotification);
                this.state = useState({
                    uiState: "LOADING", // 'LOADING' | 'READY' | 'CLOSING'
                    debugWidgetIsShown: true,
                    hasBigScrollBars: false,
                    sound: {src: null},
                    notification: {
                        isShown: false,
                        message: "",
                        duration: 2000,
                    },
                });
            }
            _onShowNotification({detail: {message, duration}}) {
                this.state.notification.isShown = true;
                this.state.notification.message = message;
                this.state.notification.duration = duration;
            }
            _onCloseNotification() {
                this.state.notification.isShown = false;
                this.state.notification.message = "";
            }
        };

    Registries.Component.extend(Chrome, NotificationChrome);

    return Chrome;
});
