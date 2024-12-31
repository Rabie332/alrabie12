from lxml import etree

from odoo import _, api, fields, models


class RequestApproval(models.Model):
    _name = "request.approval"
    _description = "Request Approval"

    # ------------------------------------------------------------
    # Fields
    # ------------------------------------------------------------
    res_model_id = fields.Many2one("ir.model", string="Model")
    image_128 = fields.Image(related="res_model_id.image_128", string="Image 128")
    image_1920 = fields.Image(
        related="res_model_id.image_128",
        max_width=1920,
        max_height=1920,
        string="Image 1920",
    )
    name = fields.Char(compute="_compute_name", translate=True, string="Name")
    kanban_color = fields.Integer(string="Kanban Color Index")
    to_approve = fields.Integer("To approve", compute="_compute_to_approve")

    # ------------------------------------------------------------
    # Compute methods
    # ------------------------------------------------------------
    @api.depends("res_model_id")
    def _compute_name(self):
        for approval in self:
            approval.name = approval.res_model_id.name

    def _compute_to_approve(self):
        """Calculate the number of requests to approve."""
        for approval in self:
            approval.to_approve = len(approval.get_activities())

    # ------------------------------------------------------------
    # Business methods
    # ------------------------------------------------------------

    def action_approve(self):
        """Return details of requests to approve from my activities."""
        objects = self.get_activities()
        return {
            "name": _("My Approvals"),
            "view_type": "form",
            "view_mode": "tree,form",
            "res_model": self.res_model_id.model,
            "view_id": False,
            "type": "ir.actions.act_window",
            "domain": [("id", "in", objects.ids)],
        }

    def get_activities(self):
        """Get requests to approve from my activities."""
        activities = (
            self.env["mail.activity"]
            .search(
                [
                    ("user_id", "=", self.env.user.id),
                    ("activity_type_id.category", "=", "validation"),
                    ("res_model_id", "=", self.res_model_id.id),
                ]
            )
            .mapped("res_id")
        )
        return self.env[self.res_model_id.model].browse(activities)

    # ------------------------------------------------------------
    # ORM methods
    # ------------------------------------------------------------

    @api.model
    def fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        """fields_view_get to remove create from Request Approval."""
        res = super(RequestApproval, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu
        )
        if self.env.context.get("no_display_create"):
            doc = etree.XML(res["arch"])
            for node in doc.xpath("//kanban"):
                node.set("create", "0")
                node.set("edit", "0")
                node.set("delete", "0")
            res["arch"] = etree.tostring(doc, encoding="unicode")
        return res
