from lxml import etree

from odoo import api, models


class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    # ------------------------------------------------------------
    # ORM methods
    # ------------------------------------------------------------

    @api.model
    def fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        """fields_view_get to remove create and edit and delete from menu payslip."""
        res = super(HrPayslip, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu
        )
        doc = etree.XML(res["arch"])
        if self.env.context.get("no_display_create"):
            for node in doc.xpath("//tree"):
                node.set("create", "0")
            for node in doc.xpath("//form"):
                node.set("create", "0")
            for node in doc.xpath("//kanban"):
                node.set("create", "0")
        res["arch"] = etree.tostring(doc, encoding="unicode")
        return res
