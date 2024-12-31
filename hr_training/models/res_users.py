from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    training_balance = fields.Integer(
        related="employee_id.training_balance", string="Training Balance"
    )
