from odoo import fields, models


class HrTrainingCenter(models.Model):
    _name = "hr.training.center"
    _description = "Training Center"

    name = fields.Char(string="Name", required=1)
    active = fields.Boolean(string="Active", default=True)
