from odoo import fields, models


class KsDashboardNinjaGridCompanyItems(models.Model):
    _name = "ks_dashboard_ninja.ks_grid_per_company"
    _description = "Dashboard Ninja Grid Per Company"

    name = fields.Char(translate=1)
    ks_dashboard_ninja_id = fields.Many2one(
        "ks_dashboard_ninja.board", string="Select Dashboard"
    )
    ks_gridstack_config = fields.Char("Item Configurations")
    ks_company_id = fields.Many2one(
        "res.company", string="Company", default=lambda self: self.env.user.company_id
    )
