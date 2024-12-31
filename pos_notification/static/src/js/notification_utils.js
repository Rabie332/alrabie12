/* eslint-disable */
odoo.define("pos_notification.notification_utils", function (require) {
    "use strict";

    function _showNotification(object, message, duration = 2000) {
        object.trigger("show-notification", {message, duration});
    }

    return {
        notification_utils: {
            showNotification: _showNotification,
        },
    };
});
