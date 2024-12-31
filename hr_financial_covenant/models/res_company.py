from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    financial_covenant_sequence_id = fields.Many2one(
        "ir.sequence",
        string="Financial Covenant Sequence",
        copy=False,
        ondelete="restrict",
    )

    @api.model
    def create(self, vals):
        """ADD sequence to company"""
        company = super(ResCompany, self).create(vals)
        IrSequence = company.env["ir.sequence"].sudo()
        val = {
            "name": "Sequence Financial Covenant " + company.name,
            "padding": 5,
            "code": "hr.financial.covenant.seq",
        }
        company.financial_covenant_sequence_id = IrSequence.create(val).id
        return company
