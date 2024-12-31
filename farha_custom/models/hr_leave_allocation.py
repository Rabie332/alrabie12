from odoo import fields, models


class HolidaysAllocation(models.Model):
    _inherit = "hr.leave.allocation"

    number_of_days_display = fields.Float(
        states={
            "draft": [("readonly", False)],
            "confirm": [("readonly", False)],
            "done": [("readonly", False)],
        }
    )
