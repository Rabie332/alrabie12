from odoo import api, models


class ReportHrCovenantResume(models.AbstractModel):
    _name = "report.hr_covenant.report_covenant_resume"
    _description = "Report Hr Covenant Resume"

    @api.model
    def _get_report_values(self, docids, data=None):
        """Get Covenants"""
        data = data if data is not None else {}
        ids = data.get("ids", [])
        docs = self.env["hr.covenant.wizard"].browse(ids)
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
        if data["form"].get("retrieval"):
            retrieval = data["form"].get("retrieval")
            domain += [("retrieval", "=", retrieval)]
        convenants = self.env["hr.covenant"].search(domain)
        return {
            "doc_ids": docids,
            "doc_model": "hr.covenant.wizard",
            "data": data,
            "docs": docs,
            "covenants": convenants,
        }
