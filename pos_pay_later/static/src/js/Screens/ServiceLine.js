/* eslint-disable */
odoo.define("point_of_sale.ServiceLine", function (require) {
    "use strict";

    const PosComponent = require("point_of_sale.PosComponent");
    const Registries = require("point_of_sale.Registries");

    class ServiceLine extends PosComponent {
        constructor() {
            super(...arguments);
        }

        get highlight() {
            return this.props.service !== this.props.selectedService ? "" : "highlight";
        }
    }
    ServiceLine.template = "ServiceLine";

    Registries.Component.add(ServiceLine);

    return ServiceLine;
});
