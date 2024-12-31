odoo.define("announcements.NotificationManager", function (require) {
    "use strict";

    // Require necessary dependencies
    var AbstractService = require("web.AbstractService");
    var core = require("web.core");
    var Dialog = require("web.Dialog");
    var rpc = require("web.rpc");

    // Define a new service called SHNotificationManager that extends AbstractService
    var SHNotificationManager = AbstractService.extend({
        dependencies: ["bus_service"], // Declare dependency on bus_service

        /**
         * @override
         * Start the service and register a listener for notifications
         */
        start: function () {
            this._super.apply(this, arguments); // Call the parent start method
            this.call("bus_service", "onNotification", this, this._onNotification); // Register notification listener
        },

        /**
         * Callback function for handling incoming notifications
         * @param {Array} notifs - Array of notifications
         */
        _onNotification: function (notifs) {
            var self = this;
            _.each(notifs, function (notif) {
                var options = {
                    model: notif[0][1], // Notification model name
                    type: notif[1].type, // Notification type
                    title: notif[1].title || "Notification", // Notification title (default if null)
                    message: notif[1].message || "No message", // Notification message (default if null)
                    id: notif[1].id, // Notification record ID
                };

                // Check if the notification is for the res.partner model and has the 'announcements_dialog' type
                if (
                    options.model === "res.partner" &&
                    options.type === "announcements_dialog"
                ) {
                    self._showDialog(options); // Show the dialog with the notification details
                }
            });
        },

        /**
         * Show a dialog with the notification details
         * @param {Object} options - Notification options
         */
        _showDialog: function (options) {
            var dialog = new Dialog(this, {
                title: options.title, // Dialog title
                message: options.message, // Dialog message
                size: "medium", // Dialog size
                $content: $("<div>").html(options.message), // Dialog content

                buttons: [
                    {
                        text: "Close",
                        classes: "btn-primary",
                        close: true,
                    },
                ],
            });

            dialog.on("closed", this, function () {
                rpc.query({
                    model: "user.notify",
                    method: "close_notify",
                    args: [options.id],
                });
            });
            dialog.open(); // Open the dialog
        },
    });

    // Register the SHNotificationManager service with the core service registry
    core.serviceRegistry.add(
        "announcements_notification_service",
        SHNotificationManager
    );

    // Return the SHNotificationManager service
    return SHNotificationManager;
});
