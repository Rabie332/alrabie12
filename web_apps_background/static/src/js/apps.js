odoo.define("web_apps_background.AppsMenu", function (require) {
    "use strict";

    var session = require("web.session");
    var AppsMenu = require("web.AppsMenu");

    AppsMenu.include({
        start: function () {
            this._setBackgroundImage();
            return this._super.apply(this, arguments);
        },
        _setBackgroundImage: function () {
            var url = session.url("/web/image", {
                model: "res.company",
                id: session.company_id,
                field: "background_image",
            });
            this.$(".dropdown-menu").css({
                "background-size": "cover",
                "background-image": "url(" + url + ")",
            });
        },
    });
});
