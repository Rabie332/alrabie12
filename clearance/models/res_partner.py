from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    # ------------------------------------------------------
    # Fields
    # ------------------------------------------------------

    is_shipping_agents = fields.Boolean(string="Shipping agent")
    code_partner = fields.Char(string="Code")
    zakat_tax_customs_authority = fields.Boolean("Zakat Tax and Customs Authority")
    property_account_container_deposit_id = fields.Many2one(
        "account.account",
        company_dependent=True,
        string="Account container deposit",
        domain="[('internal_type', '=', 'receivable'), "
        "('deprecated', '=', False), ('company_id', '=', current_company_id)]",
    )
    clearance_route_ids = fields.One2many(
        "res.partner.clearance.route", "partner_id", string="Routes"
    )
    product_ids = fields.Many2many("product.product", string="Products")
