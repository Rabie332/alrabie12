from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    clearance_sequence_id = fields.Many2one(
        "ir.sequence",
        string="Clearance Request Sequence",
        copy=False,
        ondelete="restrict",
    )
    landscape_logo = fields.Binary("Landscape Logo")

    @api.model
    def create(self, vals):
        """ADD sequence to company"""
        company = super(ResCompany, self).create(vals)
        IrSequence = company.env["ir.sequence"].sudo()
        val = {
            "name": "Sequence Clearance Request " + company.name,
            "padding": 5,
            "code": "res.company",
        }
        company.clearance_sequence_id = IrSequence.create(val).id
        return company
