from odoo.api import Environment


def migrate(cr, version):
    """Update training."""
    env = Environment(cr, 1, context={})
    training_centers = env["hr.training"].sudo().search([]).mapped("training_center")
    center_names = []
    for center in training_centers:
        if center not in center_names:
            center_names.append(center)
    for center in center_names:
        env["hr.training.center"].create({"name": center})
    for training in env["hr.training"].sudo().search([]):
        center = env["hr.training.center"].search(
            [("name", "=", training.training_center)], limit=1
        )
        if center:
            training.training_center_id = center.id
        if training.type == "internal":
            city = env["res.city"].search([("name", "=", training.city)])
            if city:
                training.city_id = city.id
