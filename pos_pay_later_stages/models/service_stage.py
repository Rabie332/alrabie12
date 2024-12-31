from odoo import fields, models


class ServiceStage(models.Model):
    """Service stages for preparing orders"""

    _name = "service.stage"
    _description = "Service Stages"
    _rec_name = "name"
    _order = "sequence, name, id"

    name = fields.Char("Stage Name", required=True, translate=True)
    sequence = fields.Integer(
        "Sequence", default=1, help="Used to order stages. Lower is better."
    )
    color = fields.Char(string="Color Index")
    fold = fields.Boolean(
        "Folded in Pipeline",
        help="This stage is folded in the kanban view "
        "when there are no records in that stage to display.",
    )
