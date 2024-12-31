from odoo import fields, models


class HrAttendanceSummaryLine(models.Model):
    _inherit = "hr.attendance.summary.line"

    def create_summary_attendance(self):
        """Update summary state when employee has leave"""
        super(HrAttendanceSummaryLine, self).create_summary_attendance()
        summary = self.env["hr.attendance.summary"].search(
            [("date", "=", fields.Date.today())]
        )
        for line_summary in summary.line_ids.filtered(
            lambda line: line.presence_state == "absent"
        ):
            # if employee has leave change state to leave
            if self.check_exist_absence_justified("hr.leave", line_summary.employee_id):
                line_summary.presence_state = "leave"

    def update_summary_attendance(self, record):
        """Update summary state when employee has leave"""
        if record._name == "hr.leave" and record.state == "done":
            # if employee has leave change state to leave
            summary_ids = self.get_summary(
                record.employee_id, record.date_from, record.date_to
            )
            if summary_ids:
                summary_ids.write({"presence_state": "leave"})
        super(HrAttendanceSummaryLine, self).update_summary_attendance(record)
