from odoo import models


class HrSalaryRequest(models.Model):
    _inherit = "hr.salary.request"

    def get_approvals_by_stage(self, stage_id):
        """Return approver name."""
        for request in self:
            stages = request.sudo().get_approvals_details()
            if stages.get(stage_id, False) and stages[stage_id]["approver"]:
                return stages[stage_id]["approver"].name
            else:
                return ""
