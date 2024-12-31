import math

from odoo import models

HEADER_VALS = [
    "رقم الطلب",
    "الرقم الوظيفي",
    "الموظف",
    "القسم",
    " تاريخ الطلب",
    "من الساعة",
    "إلى الساعة",
    "النوع",
    "عدد الساعات",
    "الوصف",
    "المرحلة",
]


class HrAuthorizationReportXls(models.AbstractModel):
    _name = "report.hr_authorization.report_hr_authorization_xlsx"
    _inherit = "report.report_xlsx.abstract"
    _description = "Hr Authorizations Reports XLS"

    def float_time_convert(self, float_val):
        """Convert float to time"""
        factor = float_val < 0 and -1 or 1
        val = abs(float_val)
        hour, minute = (factor * int(math.floor(val)), int(round((val % 1) * 60)))
        if minute == 60:
            hour = hour + 1
            minute = 0
        return "{:02d}:{:02d}".format(hour, minute)

    def _get_authorizations(self, record):
        """Get authorizations from hr.authorization model."""
        date_from = record.date_from
        date_to = record.date_to
        department_id = record.department_id.id or False
        employee_id = record.employee_id.id or False
        stage_id = record.stage_id.id or False
        domain = [
            ("date", ">=", date_from),
            ("date", "<=", date_to),
        ]
        if department_id:
            domain += [("department_id", "=", department_id)]
        if employee_id:
            domain += [("employee_id", "=", employee_id)]
        if stage_id:
            domain += [("stage_id", "=", stage_id)]
        return self.env["hr.authorization"].search(domain)

    def generate_xlsx_report(self, workbook, data, lines):
        """Generate report xlsx."""
        self = self.with_context(lang=self.env.user.lang)
        docs = self.env["hr.authorization.wizard"].browse(lines.id)
        date_from = docs.date_from
        date_to = docs.date_to
        sheet = workbook.add_worksheet("تقرير حصر الاستئذانات")
        sheet.right_to_left()
        format_sheet = workbook.add_format(
            {
                "font_size": 14,
                "font_color": "white",
                "align": "center",
                "right": True,
                "left": True,
                "bottom": True,
                "top": True,
                "bold": True,
            }
        )
        format_sheet1 = workbook.add_format(
            {
                "font_size": 14,
                "bottom": True,
                "right": True,
                "left": True,
                "top": True,
                "bold": True,
            }
        )
        format_sheet1.set_align("center")
        format_sheet1.set_align("vcenter")
        format_sheet.set_bg_color("#395870")
        font_size_8 = workbook.add_format(
            {"bottom": True, "top": True, "right": True, "left": True, "font_size": 10}
        )
        font_size_8.set_align("center")
        sheet.merge_range(
            "A1:K2",
            "تقرير حصر الاستئذانات: من  %s إلى %s" % (date_from, date_to),
            format_sheet1,
        )
        # Set header.
        prod_row = 2
        prod_col = 0
        for header_val in HEADER_VALS:
            sheet.write(prod_row, prod_col, header_val, format_sheet)
            if prod_col != 0:
                sheet.set_column(prod_row, prod_col, 25)
            else:
                sheet.set_column(prod_row, prod_col, 35)
            prod_col += 1
        prod_row += 1
        # set authorizations data
        authorizations = self._get_authorizations(docs)
        hour_numbers = 0.0
        for authorization in authorizations:
            sheet.write(prod_row, 0, authorization.name, font_size_8)
            if authorization.employee_id.number:

                sheet.write(prod_row, 1, authorization.employee_id.number, font_size_8)
            else:
                sheet.write(prod_row, 1, "-", font_size_8)
            sheet.write(prod_row, 2, authorization.employee_id.name, font_size_8)
            sheet.write(
                prod_row,
                3,
                authorization.employee_id.department_id.name,
                font_size_8,
            )
            sheet.write(
                prod_row, 4, authorization.date.strftime("%Y-%m-%d"), font_size_8
            )
            sheet.write(
                prod_row,
                5,
                self.float_time_convert(authorization.hour_start),
                font_size_8,
            )
            sheet.write(
                prod_row,
                6,
                self.float_time_convert(authorization.hour_stop),
                font_size_8,
            )
            sheet.write(prod_row, 7, authorization.request_type_id.name, font_size_8)
            sheet.write(
                prod_row,
                8,
                self.float_time_convert(authorization.duration),
                font_size_8,
            )
            hour_numbers += authorization.duration
            if authorization.description:
                sheet.write(prod_row, 9, authorization.description or "", font_size_8)
            sheet.write(prod_row, 10, authorization.stage_id.name, font_size_8)
            prod_row += 1
        prod_row += 1
        sheet.merge_range("A%s:H%s" % (prod_row, prod_row), "المجموع", format_sheet)
        sheet.write(prod_row - 1, 8, self.float_time_convert(hour_numbers), font_size_8)
        sheet.write(prod_row - 1, 9, "", font_size_8)
        sheet.write(prod_row - 1, 10, "", font_size_8)
