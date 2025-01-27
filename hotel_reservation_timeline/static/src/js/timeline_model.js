odoo.define("hotel_reservation_timeline.TimelineModel", function (require) {
    "use strict";

    const AbstractModel = require("web.AbstractModel");

    const TimelineModel = AbstractModel.extend({
        init: function () {
            this._super.apply(this, arguments);
        },

        load: function (params) {
            this.modelName = params.modelName;
            this.fieldNames = params.fieldNames;
            if (!this.preload_def) {
                this.preload_def = $.Deferred();
                $.when(
                    this._rpc({
                        model: this.modelName,
                        method: "check_access_rights",
                        args: ["write", false],
                    }),
                    this._rpc({
                        model: this.modelName,
                        method: "check_access_rights",
                        args: ["unlink", false],
                    }),
                    this._rpc({
                        model: this.modelName,
                        method: "check_access_rights",
                        args: ["create", false],
                    })
                ).then((write, unlink, create) => {
                    this.write_right = write;
                    this.unlink_right = unlink;
                    this.create_right = create;
                    this.preload_def.resolve();
                });
            }

            this.data = {
                domain: params.domain,
                context: params.context,
            };

            return this.preload_def.then(this._loadTimeline.bind(this));
        },

        /**
         * Read the records for the timeline.
         *
         * @private
         * @returns {jQuery.Deferred}
         */
        _loadTimeline: function () {
            return this._rpc({
                model: this.modelName,
                method: "search_read",
                context: this.data.context,
                fields: this.fieldNames,
                domain: this.data.domain,
            }).then((events) => {
                this.data.data = events;
                this.data.rights = {
                    unlink: this.unlink_right,
                    create: this.create_right,
                    write: this.write_right,
                };
            });
        },
    });

    return TimelineModel;
});
