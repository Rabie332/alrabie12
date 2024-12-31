from odoo import fields, models


class ResUsers(models.Model):

    _inherit = "res.users"

    partner_ids = fields.Many2many("res.partner", string="Related Customers")
