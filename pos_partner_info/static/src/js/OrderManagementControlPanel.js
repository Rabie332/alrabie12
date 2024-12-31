odoo.define("pos_partner_info.OrderManagementControlPanel", function (require) {
    "use strict";

    const Registries = require("point_of_sale.Registries");
    const OrderManagementControlPanel = require("point_of_sale.OrderManagementControlPanel");

    const CUSTOM_SEARCH_FIELDS = [
        "pos_reference",
        "partner_id.display_name",
        "partner_id.phone",
        "partner_id.ref",
        "date_order",
    ];
    // eslint-disable-next-line no-shadow
    const CustomOrderManagementControlPanel = (OrderManagementControlPanel) =>
        class extends OrderManagementControlPanel {
            get searchFields() {
                return CUSTOM_SEARCH_FIELDS;
            }
        };
    Registries.Component.extend(
        OrderManagementControlPanel,
        CustomOrderManagementControlPanel
    );
    return OrderManagementControlPanel;
});
