from odoo import fields, models

class ResUsers(models.Model):
    _inherit = 'res.users'

    user_branch_id = fields.Many2one('hotel.branch', string='User Branch')
    # _description = "User role"

    # group_id = fields.Many2one(
    #     comodel_name="res.groups",
    #     required=True,
    #     ondelete="cascade",
    #     readonly=True,
    #     string="Associated group",
    # )
