odoo.define("pos_pay_later.ServicesScreen", function (require) {
    "use strict";

    const {debounce} = owl.utils;
    const PosComponent = require("point_of_sale.PosComponent");
    const Registries = require("point_of_sale.Registries");
    const {useListener} = require("web.custom_hooks");

    class ServicesScreen extends PosComponent {
        constructor() {
            super(...arguments);
            this.state = {query: null};
            useListener("click-showDetails", this.showDetails);
            useListener("click-refresh_services", this.refresh_services);
            this.services = this.get_pos_services()[0] || [];
            this.serviceLines = this.get_pos_services()[1] || [];
            this.updateServiceList = debounce(this.updateServiceList, 70);
        }

        back() {
            this.props.resolve({confirmed: false, payload: false});
            this.trigger("close-temp-screen");
        }

        get currentOrder() {
            return this.env.pos.get_order();
        }

        get pos_services() {
            let query = this.state.query;
            if (query) {
                query = query.trim();
                query = query.toLowerCase();
            }
            if (query && query !== "") {
                return this.search_services(this.services, query);
            }
            return this.services;
        }

        get pos_order_lines() {
            return this.serviceLines;
        }

        search_services(services, query) {
            const selected_services = [];
            // Remove spaces from the search query and convert to lowercase for case-insensitive comparison
            const search_text = query.replace(/\s+/g, '').toLowerCase();
        
            services.forEach(function (service) {
                // Ensure name, pos_reference, and partner_phone are safely accessed and spaces removed for comparison
                const serviceName = service.name ? service.name.replace(/\s+/g, '').toLowerCase() : '';
                const servicePosReference = service.pos_reference ? service.pos_reference.replace(/\s+/g, '').toLowerCase() : '';
                const servicePartnerPhone = service.partner_phone ? service.partner_phone.replace(/\s+/g, '').toLowerCase() : '';
                const serviceState = service.state ? service.state.toLowerCase() : '';
                const servicePartnerName = service.partner_id && service.partner_id[1] ? service.partner_id[1].replace(/\s+/g, '').toLowerCase() : '';
        
                // Check if any field matches the search text after spaces are removed
                if (
                    serviceName.indexOf(search_text) !== -1 ||
                    servicePosReference.indexOf(search_text) !== -1 ||
                    servicePartnerPhone.indexOf(search_text) !== -1 ||
                    serviceState.indexOf(search_text) !== -1 ||
                    servicePartnerName.indexOf(search_text) !== -1
                ) {
                    selected_services.push(service);
                }
            });
            return selected_services;
        }
        
        

        refresh_services() {
            $(".input-search-services").val("");
            this.state.query = "";
            this.get_pos_services();
            this.render();
        }

        updateServiceList(event) {
            this.state.query = event.target.value;
            this.get_pos_services();
            if (this.services.length == 0) {
                this.render();
            }
        }

        get_current_day() {
            let today = new Date();
            let dd = today.getDate();
            let mm = today.getMonth() + 1; // January is 0!
            const yyyy = today.getFullYear();
            if (dd < 10) {
                dd = "0" + dd;
            }
            if (mm < 10) {
                mm = "0" + mm;
            }
            today = yyyy + "-" + mm + "-" + dd;
            return today;
        }

        async get_pos_services() {
            const self = this;
            const service_ids = [];
            try {
                await self
                    .rpc({
                        model: "pos.service",
                        method: "search_read",
                        domain: [["state", "=", "draft"]],
                    })
                    .then(function (loaded_services) {
                        self.env.pos.db.get_services_by_id = {};
                        loaded_services.forEach(function (service) {
                            service_ids.push(service.id);
                            self.env.pos.db.get_services_by_id[service.id] = service;
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

        showDetails(event) {
            const self = this;
            const o_id = parseInt(event.detail.id);
            const serviceLines = self.serviceLines;
            const pos_lines = [];

            for (let n = 0; n < serviceLines.length; n++) {
                if (serviceLines[n].service_id[0] == o_id) {
                    pos_lines.push(serviceLines[n]);
                }
            }
            self.showPopup("ServiceDetails", {
                service: event.detail,
                ServiceLines: pos_lines,
            });
        }
    }

    ServicesScreen.template = "ServicesScreen";
    Registries.Component.add(ServicesScreen);
    return ServicesScreen;
});
