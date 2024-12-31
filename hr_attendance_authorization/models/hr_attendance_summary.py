from odoo import api, fields, models


class HrAttendanceSummaryLine(models.Model):
    _inherit = "hr.attendance.summary.line"

    authorization_hours = fields.Float(
        string="Authorization",
        compute="_compute_attendance_summary",
        store=True,
    )

    def update_summary_attendance(self, record):
        """Update summary state when employee has authorization"""
        if record._name == "hr.authorization" and record.state in ["done", "cancel"]:
            summary_ids = self.get_summary(record.employee_id, record.date, record.date)
            if summary_ids:
                summary_ids._compute_attendance_summary()
        super(HrAttendanceSummaryLine, self).update_summary_attendance(record)

    @api.depends(
        "attendance_ids.check_in",
        "attendance_ids.check_out",
        "overtime_hours_manuel",
        "worked_hours_manuel",
        "delay_hours_manuel",
        "early_exit_hours",
    )
    def _compute_attendance_summary(self):
        for record in self:
            super(HrAttendanceSummaryLine, record)._compute_attendance_summary()
            record.authorization_hours = 0
            authorizations = self.env["hr.authorization"].search(
                [
                    ("employee_id", "=", record.employee_id.id),
                    ("date", "<=", record.date),
                    ("date", ">=", record.date),
                    ("state", "=", "done"),
                ]
            )
            # calculate absence_hours and authorization_hours
            if authorizations:
                record.authorization_hours = sum(authorizations.mapped("duration"))
                absence_hours = record.absence_hours - record.authorization_hours
                record.absence_hours = absence_hours if absence_hours > 0 else 0
