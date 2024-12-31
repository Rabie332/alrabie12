from odoo import fields, models


class PosNotes(models.Model):
    _name = "pos.notes"
    _description = "Notes"

    name = fields.Char(string="Name")
