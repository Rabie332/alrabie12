from odoo import models


class HrLeave(models.Model):
    _inherit = "hr.leave"

    def action_validate(self):
        res = super(HrLeave, self).action_validate()
        summary_ids = self.env["hr.attendance.summary.line"].search(
            [
                ("employee_id", "=", self.employee_id.id),
                ("date", ">=", self.request_date_from),
                ("date", "<=", self.request_date_to),
            ]
        )
        if summary_ids:
            summary_ids.write({"presence_state": "leave"})
        return res
