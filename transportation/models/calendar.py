from lxml import etree

from odoo import api, fields, models


class CalendarEvent(models.Model):
    """Model for Calendar Event"""

    _inherit = "calendar.event"

    shipping_order_id = fields.Many2one(
        "shipping.order", string="Shipping Order", index=True, ondelete="set null"
    )

    # ------------------------------------------------------
    # Business Methods
    # ------------------------------------------------------

    @api.model
    def default_get(self, fields):
        if self.env.context.get("default_shipping_order_id"):
            self = self.with_context(
                default_res_model_id=self.env.ref(
                    "transportation.model_shipping_order"
                ).id,
                default_res_id=self.env.context["default_shipping_order_id"],
            )

        defaults = super(CalendarEvent, self).default_get(fields)

        # sync res_model / res_id to opportunity id (aka creating meeting from lead chatter)
        if (
            "shipping_order_id" not in defaults
            and defaults.get("res_id")
            and (defaults.get("res_model") or defaults.get("res_model_id"))
        ):
            if (
                defaults.get("res_model") and defaults["res_model"] == "shipping.order"
            ) or (
                defaults.get("res_model_id")
                and self.env["ir.model"].sudo().browse(defaults["res_model_id"]).model
                == "shipping.order"
            ):
                defaults["shipping_order_id"] = defaults["res_id"]

        return defaults

    @api.model
    def fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        """fields_view_get no create and edit in calendar."""
        res = super(CalendarEvent, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu
        )
        if self.env.context.get("default_no_create_edit"):
            doc = etree.XML(res["arch"])
            for node in doc.xpath("//calendar"):
                node.set("create", "0")
                node.set("edit", "0")
                node.set("delete", "0")
            for node in doc.xpath("//tree"):
                node.set("create", "0")
                node.set("edit", "0")
                node.set("delete", "0")
            for node in doc.xpath("//form"):
                node.set("create", "0")
                node.set("edit", "0")
                node.set("delete", "0")
            res["arch"] = etree.tostring(doc, encoding="unicode")
        return res

    # ------------------------------------------------------------
    # Compute methods
    # ------------------------------------------------------------

    def _compute_is_highlighted(self):
        super(CalendarEvent, self)._compute_is_highlighted()
        shipping_order_id = self.env.context.get("active_id")
        if (
            self.env.context.get("active_model") == "shipping.order"
            and shipping_order_id
        ):
            for event in self:
                if event.shipping_order_id.id == shipping_order_id:
                    event.is_highlighted = True
