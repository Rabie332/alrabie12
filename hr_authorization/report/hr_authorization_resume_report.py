from odoo import api, models


class ReportHrAuthorizationResume(models.AbstractModel):
    _name = "report.hr_authorization.report_hr_authorization_resume"
    _description = "Report Hr Authorization Resume"

    @api.model
    def _get_report_values(self, docids, data=None):
        """Get Authorizations"""
        data = data if data is not None else {}
        ids = data.get("ids", [])
        docs = self.env["hr.authorization.wizard"].browse(ids)
        date_from = data["form"].get("date_from")
        date_to = data["form"].get("date_to")
        domain = [
            (("date", ">=", date_from)),
            (("date", "<=", date_to)),
        ]
        if data["form"].get("department_id"):
            department_id = data["form"].get("department_id")[0]
            domain += [("department_id", "=", department_id)]
        if data["form"].get("employee_id"):
            employee_id = data["form"].get("employee_id")[0]
            domain += [("employee_id", "=", employee_id)]
        if data["form"].get("stage_id"):
            stage_id = data["form"].get("stage_id")[0]
            domain += [("stage_id", "=", stage_id)]
        authorizations = self.env["hr.authorization"].search(domain)
        return {
            "doc_ids": docids,
            "doc_model": "hr.attendance.wizard",
            "data": data,
            "docs": docs,
            "hr_authorizations": authorizations,
        }
