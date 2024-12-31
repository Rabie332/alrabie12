import base64

from odoo import _, api, fields, models


class HrAttendanceReport(models.TransientModel):
    _name = "hr.attendance.report"
    _rec_name = "employee_id"
    _description = "Attendance Report"

    date_from = fields.Date(string="From", required=1)
    date_to = fields.Date(string="To", required=1)
    employee_id = fields.Many2one("hr.employee", string="Employee")
    department_id = fields.Many2one("hr.department", string="Department")

    @api.onchange("department_id")
    def _onchange_department_id(self):
        employees = self.env["hr.employee"].search([])
        if self.department_id:
            employees = self.env["hr.employee"].search(
                [("department_id", "=", self.department_id.id)]
            )
        return {"domain": {"employee_id": [("id", "in", employees.ids)]}}

    def print_attendance_summary_report(self):
        """Print evaluation report."""
        data = {"ids": [self.id], "form": self.read([])[0]}
        return self.env.ref(
            "hr_attendance_summary.hr_attendance_summary_report"
        ).report_action(self, data=data)

    def print_summary_xls_report(self):
        """Print evaluation report XlSX."""
        data = {"ids": [self.id], "form": self.read([])[0]}
        self.env.ref(
            "hr_attendance_summary.hr_attendance_summary_report_xlsx"
        ).sudo().report_file = _("Attendance Summary Report")
        return self.env.ref(
            "hr_attendance_summary.hr_attendance_summary_report_xlsx"
        ).report_action(self, data=data)

    def get_employee_summary(self):
        """Get employees from summary."""
        domain = []
        if self.department_id:
            domain.append(("employee_id.department_id", "=", self.department_id.id))
        if self.employee_id:
            domain.append(("employee_id", "=", self.employee_id.id))
        summarys = self.env["hr.attendance.summary.line"].search(
            [
                ("summary_id.date", ">=", self.date_from),
                ("summary_id.date", "<=", self.date_to),
            ]
            + domain
        )
        return summarys.mapped("employee_id")

    def prepare_mail_values(self, employee, attachment):
        """Prepare mail values."""
        return {
            "subject": _("Attendance Summary Report"),
            "body_html": _(
                "<div> <h4>Hello %s  </h4><br /><br />"
                "the Attendance Summary Report has been attached to you,"
                "We also inform you of the following: "
                "<ul><li>Worked hours are considered only between 9AM and 5PM. </li>"
                "<li> If there is only one fingerprint, whether, for entry or exit, "
                "you will be considered that you worked only half "
                "of the day, which are four hours. </li>"
                "<li>Absences days will be deducted. </li>"
                "<li>Late hours will be deducted. </li>"
                "<li>You will find everything mentioned in the system,"
                " including permissions and deputation, in the notes.</li>"
                "<li>We hope that you will add the hours of delay, "
                "early departure or leaves in the system, "
                "and if there is no justification within two working days,"
                " it will be deducted according to the system.</li></ul>"
                "<br /> If you have any questions or comments, we are happy to contact you. "
                "<br /> <h4>Cordially </h4>"
                "<br /></div>"
            )
            % employee.name,
            "author_id": self.env.user.partner_id.id,
            "email_from": self.env.company.email or self.env.user.email_formatted,
            "email_to": employee.work_email,
            "attachment_ids": [(4, attachment.id)],
        }

    def create_attachment(self, employee):
        """Create Attachment."""
        data = {"ids": [self.id], "form": self.read([])[0]}
        self.employee_id = employee.id
        report = self.env.ref(
            "hr_attendance_summary.hr_attendance_summary_report"
        )._render_qweb_pdf(self, data=data)
        filename = "Attendance_Summary_Report.pdf"
        attachment = self.env["ir.attachment"].create(
            {
                "name": filename,
                "type": "binary",
                "datas": base64.b64encode(report[0]),
                "res_model": "hr.attendance.report",
                "res_id": self.ids[0],
                "mimetype": "application/x-pdf",
            }
        )
        return attachment

    def send_mail_summary_report(self):
        """Send mails to employees"""
        # create attachment

        # send mail
        for employee in self.get_employee_summary():
            if employee.work_email:
                attachment = self.create_attachment(employee)
                mail = (
                    self.env["mail.mail"]
                    .sudo()
                    .create(self.prepare_mail_values(employee, attachment))
                )
                mail.send()
