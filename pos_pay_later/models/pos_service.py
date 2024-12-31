from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)

class PosServer(models.Model):
    _name = "pos.service"
    _inherit = "pos.order"
    _description = "POS service"
    _order = "date_order desc"

    service_line_ids = fields.One2many(
        "pos.order.line",
        "service_id",
        string="Service Lines",
        states={"draft": [("readonly", False)]},
        readonly=True,
        copy=True,
    )
    partner_phone = fields.Char("Phone", related="partner_id.phone")

    def _order_fields(self, ui_order):
        res = super(PosServer, self)._order_fields(ui_order)
        if self._name == "pos.service":
            service_line_ids = res.get("lines")
            res.pop("lines")
            res["service_line_ids"] = service_line_ids
        return res

    @api.model
    def create_service_from_ui(self, services, draft=False):
        """Create and update services from the frontend PoS application."""
        order_ids = []
        for service in services:
            existing_order = False
            if "server_id" in service["data"]:
                existing_order = self.env["pos.service"].search(
                    [
                        "|",
                        ("id", "=", service["data"]["server_id"]),
                        ("pos_reference", "=", service["data"]["name"]),
                    ],
                    limit=1,
                )
            if (
                existing_order and existing_order.state == "draft"
            ) or not existing_order:
                order_ids.append(self._process_order(service, draft, existing_order))

        return self.env["pos.service"].search_read(
            domain=[("id", "in", order_ids)], fields=["id", "pos_reference"]
        )

    def set_service_state_done(self):
        """Set service state to 'Done' by finding the stage with sequence 7."""
        for record in self:
            stage = self.env['service.stage'].search([('sequence', '=', 7)], limit=1)
            if stage:
                record.write({'state': 'paid', 'service_stage_id': stage.id})
            else:
                _logger.error("No service stage with sequence 7 found.")

class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    service_id = fields.Many2one(
        "pos.service",
        string="Service Ref",
        ondelete="cascade",
        index=True,
    )
    order_id = fields.Many2one(required=False)