from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    shipping_order_sequence_id = fields.Many2one(
        "ir.sequence",
        string="Shipping Order Sequence",
        copy=False,
        ondelete="restrict",
    )

    # ------------------------------------------------------
    # ORM Methods
    # ------------------------------------------------------

    @api.model
    def create(self, vals):
        """ADD sequence to company"""
        company = super(ResCompany, self).create(vals)
        IrSequence = company.env["ir.sequence"].sudo()
        val = {
            "name": "Shipping Order " + company.name,
            "padding": 5,
            "code": "res.company",
        }
        company.shipping_order_sequence_id = IrSequence.create(val).id
        return company
