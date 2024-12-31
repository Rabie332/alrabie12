from odoo import api, fields, models


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    summary_id = fields.Many2one("hr.attendance.summary.line", string="Summary")

    def check_exist_summary(self, employee, date):
        attendance_summary_line_obj = self.env["hr.attendance.summary.line"]
        summary_line = attendance_summary_line_obj.search(
            [("employee_id", "=", employee.id), ("date", "=", date)]
        )
        if not summary_line:
            attendance_summary_obj = self.env["hr.attendance.summary"]
            summary = attendance_summary_obj.search([("date", "=", date)])
            if not summary:
                summary = attendance_summary_obj.create({"date": date})
            summary_line = attendance_summary_line_obj.create(
                {"employee_id": employee.id, "date": date, "summary_id": summary.id}
            )
        return summary_line

    @api.model
    def create(self, values):
        res = super(HrAttendance, self).create(values)
        summary_line = self.check_exist_summary(res.employee_id, res.check_in.date())
        if summary_line:
            res.summary_id = summary_line.id
            summary_line.presence_state = "service"
        return res
