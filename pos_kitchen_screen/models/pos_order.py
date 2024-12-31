from odoo import api, fields, models


class PosOrder(models.Model):
    _inherit = "pos.order"

    def _default_stage_id(self):
        if self.env.ref("pos_kitchen_screen.stage_new", False):
            return self.env.ref("pos_kitchen_screen.stage_new").id

    stage_id = fields.Many2one(
        "kitchen.stage",
        default=_default_stage_id,
        group_expand="_read_group_stage_ids",
    )

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        """Always display all stages"""
        return stages.search([], order=order)
