from odoo import api, fields, models


class PosService(models.Model):
    _inherit = "pos.service"

    def _default_stage_id(self):
        if self.env.ref("pos_pay_later_stages.stage_new", False):
            return self.env.ref("pos_pay_later_stages.stage_new").id

    service_stage_id = fields.Many2one(
        "service.stage",
        default=_default_stage_id,
        group_expand="_read_group_stage_ids",
    )
    service_stage_color = fields.Char("color", related="service_stage_id.color")

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        """Always display all stages"""
        return stages.search([], order=order)
