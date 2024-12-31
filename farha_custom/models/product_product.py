from lxml import etree

from odoo import api, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.model
    def fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        """fields_view_get to remove create/edit af product template."""
        res = super(ProductTemplate, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu
        )
        if not self.env.user.has_group("farha_custom.group_create_product"):
            doc = etree.XML(res["arch"])
            for node in doc.xpath("//kanban"):
                node.set("create", "false")
                node.set("edit", "false")
                node.set("delete", "false")
            for node in doc.xpath("//tree"):
                node.set("create", "false")
                node.set("edit", "false")
                node.set("delete", "false")
            for node in doc.xpath("//form"):
                node.set("create", "false")
                node.set("edit", "false")
                node.set("delete", "false")
            res["arch"] = etree.tostring(doc, encoding="unicode")
        return res


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model
    def fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        """fields_view_get to remove create/edit of product."""
        res = super(ProductProduct, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu
        )
        if not self.env.user.has_group("farha_custom.group_create_product"):
            doc = etree.XML(res["arch"])
            for node in doc.xpath("//kanban"):
                node.set("create", "false")
                node.set("edit", "false")
                node.set("delete", "false")
            for node in doc.xpath("//tree"):
                node.set("create", "false")
                node.set("edit", "false")
                node.set("delete", "false")
            for node in doc.xpath("//form"):
                node.set("create", "false")
                node.set("edit", "false")
                node.set("delete", "false")
            res["arch"] = etree.tostring(doc, encoding="unicode")
        return res
