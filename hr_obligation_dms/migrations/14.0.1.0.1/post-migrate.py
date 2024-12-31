from odoo.api import Environment


def migrate(cr, version):
    """Attach documents to obligation."""
    env = Environment(cr, 1, context={})

    obligation = env["hr.obligation.setting"].search([], limit=1)
    obligation.mapped("folder_ids.documents_ids").write(
        {"res_id": obligation.id, "res_model": "hr.obligation.setting"}
    )
