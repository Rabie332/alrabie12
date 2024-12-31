from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    mol_establishment = fields.Char(string="Mol Establishment")
