/* eslint-disable */
odoo.define("pos_partner_info.OrderManagementScreen", function (require) {
    "use strict";

    const Registries = require("point_of_sale.Registries");
    const {Gui} = require("point_of_sale.Gui");
    const {isRpcError} = require("point_of_sale.utils");
    const OrderFetcher = require("point_of_sale.OrderFetcher");
    const OrderManagementScreen = require("point_of_sale.OrderManagementScreen");

    // eslint-disable-next-line no-shadow
    const CustomOrderManagementScreen = (OrderManagementScreen) =>
        class extends OrderManagementScreen {
            _onSearch({detail: domain}) {
                OrderFetcher.setSearchDomain(domain);
                OrderFetcher.setPage(1);
                var activeOrders = this._get_active_orders(OrderFetcher);
                this._custom_orders_fetch(OrderFetcher, activeOrders);
            }
            _get_active_orders(order_fetcher) {
                var self = this;
                const allActiveOrders = this.env.pos.get("orders").models;
                return order_fetcher.searchDomain
                    ? allActiveOrders.filter(
                          self._predicateBasedOnSearchDomain.bind(this)
                      )
                    : allActiveOrders;
            }
            _predicateBasedOnSearchDomain(order) {
                function check(order, field, searchWord) {
                    searchWord = searchWord.toLowerCase();
                    // Start patch
                    const client = order.get_client();
                    // End patch
                    switch (field) {
                        case "pos_reference":
                            return order.name.toLowerCase().includes(searchWord);
                        case "partner_id.display_name":
                            return client
                                ? client.name.toLowerCase().includes(searchWord)
                                : false;
                        // Start patch
                        case "partner_id.ref":
                            return client
                                ? client.ref.toLowerCase().includes(searchWord)
                                : false;
                        case "partner_id.phone":
                            return client
                                ? client.phone.toLowerCase().includes(searchWord)
                                : false;
                        // End patch
                        case "date_order":
                            return moment(order.creation_date)
                                .format("YYYY-MM-DD hh:mm A")
                                .includes(searchWord);
                        default:
                            return false;
                    }
                }
                for (let [field, _, searchWord] of (
                    OrderFetcher.searchDomain || []
                ).filter((item) => item !== "|")) {
                    // Remove surrounding "%" from `searchWord`
                    searchWord = searchWord.substring(1, searchWord.length - 1);
                    if (check(order, field, searchWord)) {
                        return true;
                    }
                }
                return false;
            }
            async _custom_orders_fetch(order_fetcher, activeOrders) {
                try {
                    let limit = 0,
                        offset = 0;
                    let start = 0,
                        end = 0;
                    if (
                        order_fetcher.currentPage <=
                        order_fetcher.lastPageFullOfActiveOrders
                    ) {
                        // Show only active orders.
                        start =
                            (order_fetcher.currentPage - 1) * order_fetcher.nPerPage;
                        end = order_fetcher.currentPage * order_fetcher.nPerPage;
                        order_fetcher.ordersToShow = activeOrders.slice(start, end);
                    } else if (
                        order_fetcher.currentPage ===
                        order_fetcher.lastPageFullOfActiveOrders + 1
                    ) {
                        // Show partially the remaining active orders and
                        // some orders from the backend.
                        offset = 0;
                        limit =
                            order_fetcher.nPerPage -
                            order_fetcher.remainingActiveOrders;
                        start =
                            (order_fetcher.currentPage - 1) * order_fetcher.nPerPage;
                        end = activeOrders.length;
                        order_fetcher.ordersToShow = [
                            ...activeOrders.slice(start, end),
                            ...(await order_fetcher._fetch(limit, offset)),
                        ];
                    } else {
                        // Show orders from the backend.
                        offset =
                            order_fetcher.nPerPage -
                            order_fetcher.remainingActiveOrders +
                            (order_fetcher.currentPage -
                                (order_fetcher.lastPageFullOfActiveOrders + 1) -
                                1) *
                                order_fetcher.nPerPage;
                        limit = order_fetcher.nPerPage;
                        order_fetcher.ordersToShow = await order_fetcher._fetch(
                            limit,
                            offset
                        );
                    }
                    order_fetcher.trigger("update");
                } catch (error) {
                    if (isRpcError(error) && error.message.code < 0) {
                        Gui.showPopup("ErrorPopup", {
                            title: order_fetcher.comp.env._t("Network Error"),
                            body: order_fetcher.comp.env._t(
                                "Unable to fetch orders if offline."
                            ),
                        });
                        Gui.setSyncStatus("error");
                    } else {
                        throw error;
                    }
                }
            }
        };
    Registries.Component.extend(OrderManagementScreen, CustomOrderManagementScreen);
});
