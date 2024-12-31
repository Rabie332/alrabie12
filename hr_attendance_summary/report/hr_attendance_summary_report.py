from odoo import api, models


class AttendanceSummaryReport(models.AbstractModel):
    _name = "report.hr_attendance_summary.hr_attendance_summary_template"
    _description = "Attendance Summary Reports"

    def _get_lines(self, data):
        department_id = (
            data["department_id"]
            and data["department_id"][0]
            and data["department_id"][0].id
            or False
        )
        employee_id = (
            data["employee_id"]
            and data["employee_id"][0]
            and data["employee_id"][0].id
            or False
        )
        domain = [
            ("summary_id.date", ">=", data["date_from"]),
            ("summary_id.date", "<=", data["date_to"]),
        ]
        if department_id:
            domain.append(("employee_id.department_id", "=", department_id))
        if employee_id:
            domain.append(("employee_id", "=", employee_id))
        summaries = self.env["hr.attendance.summary.line"].search(domain)
        return summaries

    @api.model
    def _get_report_values(self, docids, data=None):
        """Get report values."""
        data = data if data is not None else {}
        ids = data.get("ids", [])
        docs = self.env["hr.attendance.report"].browse(ids)
        return {
            "doc_ids": docids,
            "doc_model": "hr.attendance.report",
            "data": data,
            "docs": docs,
            "get_lines": self._get_lines,
        }
