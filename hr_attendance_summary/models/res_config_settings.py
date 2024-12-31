from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    group_attendance_manual_pointing = fields.Boolean(
        string="Manual pointing",
        implied_group="hr_attendance_summary.group_manual_pointing",
    )
