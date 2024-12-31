from odoo.api import Environment


def migrate(cr, version):
    """Update training."""
    env = Environment(cr, 1, context={})
    training_center = (
        env["hr.training.center"]
        .sudo()
        .search([("name", "=", "مركز غرفة الشرقية للتدريب")], limit=1)
    )
    training_centers = (
        env["hr.training.center"]
        .sudo()
        .search(
            [
                (
                    "name",
                    "in",
                    [
                        "مركز التدريب غرفة الشرقية",
                        "مركز غرفة الشرقيه",
                        "مركز التدريب - غرفة الشرقية",
                        "غرفة الشرقية",
                        "مركز غرفة الشرقية للتدريب",
                    ],
                )
            ],
            limit=1,
        )
    )
    for training in (
        env["hr.training"]
        .sudo()
        .search([("training_center_id", "in", training_centers.ids)])
    ):
        if training_center:
            training.training_center_id = training_center.id
