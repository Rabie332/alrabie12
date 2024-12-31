/* eslint-disable */
odoo.define("pos_cash_atm.Chrome", function (require) {
    "use strict";

    const Chrome = require("point_of_sale.Chrome");
    const Registries = require("point_of_sale.Registries");
    const {posbus} = require("point_of_sale.utils");
    const Session = require("web.Session");
    const framework = require("web.framework");
    const field_utils = require("web.field_utils");
    const core = require("web.core");
    const QWeb = core.qweb;
    var _t = core._t;

    const PosChrome = (Chrome) =>
        class extends Chrome {
            constructor() {
                super(...arguments);
            }

            async closingSession() {
                framework.blockUI();
                const closingSession = await this.rpc({
                    model: "pos.session",
                    method: "force_action_pos_session_close",
                    args: [[this.env.pos.pos_session.id]],
                });
                framework.unblockUI();
                return closingSession;
            }
            __closePopup() {
                super.__closePopup();
                posbus.trigger("closed-popup");
            }

            async _setCashAtm() {
                await this.rpc({
                    model: "pos.session",
                    method: "update_cash_session",
                    args: [this.env.pos.pos_session.id, cash.value, atm.value],
                });
            }

            async _closePos() {
                const ordersUnpaid = this.env.pos.db.get_unpaid_orders();
                const iot_url = this.env.pos.session.origin;
                const connection = new Session(void 0, iot_url, {
                    use_cors: true,
                });
                const self = this;

                const state = await this.rpc({
                    model: "pos.session",
                    method: "get_state",
                    args: [this.env.pos.pos_session.id],
                });
                var hidden = false;
                if (state == "closed") {
                    hidden = true;
                }
                const lists = [
                    {
                        name: this.env._t("Keep Session"),
                        item: 0,
                        id: 0,
                        hidden: hidden,
                    },
                    {
                        name: this.env._t("Close Session"),
                        item: 1,
                        id: 1,
                        hidden: hidden,
                    },
                    {
                        name: this.env._t("Close Session/Logout"),
                        item: 2,
                        id: 2,
                        hidden: hidden,
                    },
                    {
                        name: this.env._t("Logout System"),
                        item: 3,
                        id: 3,
                        hidden: hidden,
                    },
                    {
                        name: this.env._t("Back"),
                        item: 4,
                        id: 4,
                        hidden: !hidden,
                    },
                ];
                const {confirmed, payload: selectedCloseTypes} = await this.showPopup(
                    "PopUpSelectionBox",
                    {
                        items: lists,
                        onlySelectOne: true,
                    }
                );

                if (
                    confirmed &&
                    selectedCloseTypes.items &&
                    selectedCloseTypes.items.length == 1
                ) {
                    const typeId = selectedCloseTypes.items[0].id;

                    if (typeId == 4) {
                        return (window.location =
                            "/web?#id=" +
                            this.env.pos.pos_session.id +
                            "&model=pos.session&view_type=form");
                    }
                    if ((cash.value && cash) || (atm.value && atm)) {
                        if (typeId == 0) {
                            await this._setCashAtm();
                            return super._closePos();
                        }
                        if (typeId == 1) {
                            await this._setCashAtm();
                            await this.closingSession();
                            const params = {
                                model: "pos.session",
                                method: "build_sessions_report",
                                args: [[this.env.pos.pos_session.id]],
                            };
                            const values = await this.rpc(params, {shadow: true}).then(
                                function (values) {
                                    return values;
                                }
                            );

                            const reportData = values[this.env.pos.pos_session.id];
                            let start_at = field_utils.parse.datetime(
                                reportData.session.start_at
                            );
                            start_at = field_utils.format.datetime(start_at);
                            reportData.start_at = start_at;
                            if (reportData.stop_at) {
                                var stop_at = field_utils.parse.datetime(
                                    reportData.session.stop_at
                                );
                                stop_at = field_utils.format.datetime(stop_at);
                                reportData.stop_at = stop_at;
                            }
                            const reportHtml = QWeb.render(
                                "ReportSalesSummarySession",
                                {
                                    pos: this.env.pos,
                                    report: reportData,
                                }
                            );

                            this.showScreen("ReportScreen", {
                                report_html: reportHtml,
                                closeScreen: true,
                            });
                        }
                        if (typeId == 2) {
                            await this._setCashAtm();
                            await this.closingSession();
                            return (window.location = "/web/session/logout");
                        }
                        if (typeId == 3) {
                            await this._setCashAtm();
                            return (window.location = "/web/session/logout");
                        }
                    } else {
                        alert(_t("You should add Cash or ATM."));
                        this._closePos();
                    }
                }
            }
        };
    Registries.Component.extend(Chrome, PosChrome);

    return PosChrome;
});
