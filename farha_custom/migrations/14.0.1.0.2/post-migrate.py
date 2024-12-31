from odoo.api import Environment


def migrate(cr, version):
    """Update Fleet license expiry date."""
    env = Environment(cr, 1, context={})
    for employee in (
        env["hr.employee"]
        .sudo()
        .search(
            [
                ("driving_license_end_date", "!=", False),
                ("address_home_id", "!=", False),
            ]
        )
    ):
        fleet = env["fleet.vehicle"].search(
            [("driver_id", "=", employee.address_home_id.id)]
        )
        if fleet:
            fleet.driver_license_expiry_date = employee.driving_license_end_date
