from odoo import _
from odoo.api import Environment


def migrate(cr, version):
    """Add overtime setting."""
    env = Environment(cr, 1, context={})
    overtime_mandate = env["hr.overtime.setting"].search([("type", "=", "mandate")])
    overtime = env["hr.overtime.setting"].search([("type", "=", "overtime")])
    if not overtime_mandate:
        overtime_mandate = env["hr.overtime.setting"].search([], limit=1)
        if overtime_mandate:
            overtime_mandate.type = "mandate"
    if not overtime:
        env["hr.overtime.setting"].create(
            {
                "type": "overtime",
                "name": _("Overtime Setting"),
                "min_hour_day": 2,
                "max_hour_day": 3,
                "min_hour_weekend": 2,
                "max_hour_weekend": 8,
                "max_hour_month": 50,
            }
        )
