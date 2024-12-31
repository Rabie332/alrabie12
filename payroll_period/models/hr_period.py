from odoo import fields, models


class HrPeriod(models.Model):
    _inherit = "hr.period"

    number_worked_days = fields.Integer(
        "Number work days", states={"draft": [("readonly", False)]}
    )
    number_worked_hours = fields.Float(
        "Number work hours", states={"draft": [("readonly", False)]}
    )
