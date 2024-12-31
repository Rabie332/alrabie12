/* eslint-disable */
odoo.define("pos_pay_later_stages.ServicesScreen", function (require) {
    "use strict";

    const Registries = require("point_of_sale.Registries");
    const ServicesScreen = require("pos_pay_later.ServicesScreen");

    const StagesServicesScreen = (ServicesScreen) =>
        class extends ServicesScreen {
            async get_pos_services() {
                const self = this;
                const service_ids = [];
                try {
                    await self
                        .rpc({
                            model: "pos.service",
                            method: "search_read",
                            domain: [["service_stage_id.fold", "=", false]],
                        })
                        .then(function (loaded_services) {
                            self.env.pos.db.get_services_by_id = {};
                            loaded_services.forEach(function (service) {
                                service_ids.push(service.id);
                                self.env.pos.db.get_services_by_id[
                                    service.id
                                ] = service;
                            });
                            self.rpc({
                                model: "pos.order.line",
                                method: "search_read",
                                domain: [["service_id", "in", service_ids]],
                            }).then(function (service_lines) {
                                self.services = loaded_services;
                                self.serviceLines = service_lines;
                                self.render();
                                return [loaded_services, service_lines];
                            });
                        });
                } catch (error) {
                    if (error.message.code < 0) {
                        await this.showPopup("OfflineErrorPopup", {
                            title: this.env._t("Offline"),
                            body: this.env._t("Unable to load services."),
                        });
                    } else {
                        throw error;
                    }
                }
            }
        };
    Registries.Component.extend(ServicesScreen, StagesServicesScreen);
    return ServicesScreen;
});
