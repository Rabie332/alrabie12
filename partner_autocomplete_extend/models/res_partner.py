from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"
    _order = "name"

    name = fields.Char(translate=True)
    display_name = fields.Char(store=False, search="_search_display_name")

    def _search_display_name(self, operator, value):
        partners = self.search([("name", operator, value)])
        return [("id", "=", partners.ids)]
