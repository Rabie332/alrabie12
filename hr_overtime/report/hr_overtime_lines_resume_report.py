from odoo import api, models


class ReportHrOvertimeLinesResume(models.AbstractModel):
    _name = "report.hr_overtime.report_hr_overtime_lines_resume"
    _description = "Report Hr Overtime Lines Resume"

    def _get_lines(self, data):
        """Get overtime lines"""
        date_from = data["date_from"]
        date_to = data["date_to"]
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
        stage_id = (
            data["stage_id"] and data["stage_id"][0] and data["stage_id"][0].id or False
        )
        domain = [
            (("date", ">=", date_from)),
            (("date", "<=", date_to)),
        ]
        if department_id:
            domain += [("overtime_id.department_id", "=", department_id)]
        if employee_id:
            domain += [("overtime_id.employee_id", "=", employee_id)]
        if stage_id:
            domain += [("overtime_id.stage_id", "=", stage_id)]
        overtimes_lines = self.env["hr.overtime.line"].sudo().search(domain)
        return overtimes_lines

    @api.model
    def _get_report_values(self, docids, data=None):
        """Get report values."""
        data = data if data is not None else {}
        ids = data.get("ids", [])
        docs = self.env["hr.overtime.wizard"].browse(ids)
        return {
            "doc_ids": docids,
            "doc_model": "hr.overtime.wizard",
            "data": data,
            "docs": docs,
            "get_lines": self._get_lines,
        }
