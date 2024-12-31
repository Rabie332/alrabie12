from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    sequence_id = fields.Many2one(
        "ir.sequence",
        string="Employee Category Sequence",
        copy=False,
        ondelete="restrict",
    )

    @api.model
    def create(self, vals):
        """Add  company sequence."""
        company = super(ResCompany, self).create(vals)
        if company and not company.sequence_id:
            IrSequence = company.env["ir.sequence"].sudo()
            val = {
                "name": company.name,
                "padding": 5,
                "code": "res.company",
                "company_id": company.id,
            }
            company.sequence_id = IrSequence.create(val).id
        return company
