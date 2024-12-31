from odoo.api import Environment


def migrate(cr, version):
    """Attach employee to attachment."""
    env = Environment(cr, 1, context={})
    for employee in (
        env["hr.employee"]
        .sudo()
        .with_context(active_test=False)
        .search(
            [
                "|",
                "|",
                "|",
                ("attachment_ids", "!=", False),
                ("health_certificate_attachment_ids", "!=", False),
                ("driving_license_attachment_ids", "!=", False),
                ("insurance_attachment_ids", "!=", False),
            ]
        )
    ):
        employee.attachment_ids.write({"res_id": employee.id})
        employee.health_certificate_attachment_ids.write({"res_id": employee.id})
        employee.driving_license_attachment_ids.write({"res_id": employee.id})
        employee.insurance_attachment_ids.write({"res_id": employee.id})
