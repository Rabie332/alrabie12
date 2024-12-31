import math
from datetime import datetime

import pytz

from odoo import _, models

HEADER_VALS1 = [
    "الموظف",
    "الادارة",
    "التاريخ",
    "الدخول",
    "الخروج",
    "تأخير",
    "وقت إضافي",
    "ساعات الغياب",
    "ساعات العمل",
    "حالة الحضور",
    "حالة إكتمال ساعات العمل",
]


class AttendanceSummaryReportXls(models.AbstractModel):
    _name = "report.hr_attendance_summary.report_attendance_summary_xlsx"
    _inherit = "report.report_xlsx.abstract"
    _description = "Attendance Summary Reports XLS"

    def float_time_convert(self, float_val):
        factor = float_val < 0 and -1 or 1
        val = abs(float_val)
        hour, minute = (factor * int(math.floor(val)), int(round((val % 1) * 60)))
        if minute == 60:
            hour = hour + 1
            minute = 0
        return "{:02d}:{:02d}".format(hour, minute)

    def _get_lines(self, record):
        """Get report's lines from hr.attendance model."""
        date_from = record.date_from
        date_to = record.date_to
        department_id = record.department_id.id or False
        employee_id = record.employee_id.id or False
        domain = [
            ("summary_id.date", ">=", date_from),
            ("summary_id.date", "<=", date_to),
        ]
        if department_id:
            domain.append(("employee_id.department_id", "=", department_id))
        if employee_id:
            domain.append(("employee_id", "=", employee_id))
        return self.env["hr.attendance.summary.line"].search(domain)

    def generate_xlsx_report(self, workbook, data, lines):
        """Generate report xlsx."""
        docs = self.env["hr.attendance.report"].browse(lines.id)
        date_from = docs.date_from
        date_to = docs.date_to
        sheet = workbook.add_worksheet("تقرير الحضور والإنصراف")
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
        cell_format_center = workbook.add_format(
            {"bottom": True, "top": True, "right": True, "left": True, "font_size": 10}
        )
        cell_format_center.set_align("center")
        cell_format = workbook.add_format(
            {"bottom": True, "top": True, "right": True, "left": True, "font_size": 10}
        )
        cell_format.set_align("right")
        sheet.merge_range(
            "A1:K2",
            "تقرير الحضور والإنصراف: من  {} إلى {}".format(date_from, date_to),
            format_sheet1,
        )
        # Set header
        prod_row = 2
        prod_col = 0
        for header_val in HEADER_VALS1:
            sheet.write(prod_row, prod_col, header_val, format_sheet)
            sheet.set_column(prod_row, prod_col, len(header_val) * 2)
            prod_col += 1
        prod_row += 1
        # set lines
        lines = self._get_lines(docs)
        user_tz = self.env.user.tz or pytz.utc
        local = pytz.timezone(user_tz)
        for line in lines:
            format_absence_justified = workbook.add_format(
                {
                    "bottom": True,
                    "top": True,
                    "right": True,
                    "left": True,
                    "font_size": 10,
                }
            )
            format_absence_justified.set_align("center")
            sheet.write(prod_row, 0, line.employee_id.name, cell_format_center)
            sheet.write(
                prod_row,
                1,
                line.employee_id.department_id.name
                if line.employee_id.department_id
                else "",
                cell_format_center,
            )
            sheet.write(prod_row, 2, line.date.strftime("%Y-%m-%d"), cell_format_center)

            check_in_date = (
                datetime.strftime(
                    pytz.utc.localize(
                        datetime.strptime(str(line.check_in_date), "%Y-%m-%d %H:%M:%S")
                    ).astimezone(local),
                    "%H:%M:%S",
                )
                if line.check_in_date
                else False
            )

            sheet.write(
                prod_row,
                3,
                check_in_date if check_in_date else "-",
                cell_format_center,
            )
            check_out_date = (
                datetime.strftime(
                    pytz.utc.localize(
                        datetime.strptime(str(line.check_out_date), "%Y-%m-%d %H:%M:%S")
                    ).astimezone(local),
                    "%H:%M:%S",
                )
                if line.check_out_date
                else False
            )
            sheet.write(
                prod_row,
                4,
                check_out_date if check_out_date else "-",
                cell_format_center,
            )
            sheet.write(
                prod_row,
                5,
                self.float_time_convert(line.delay_hours),
                cell_format_center,
            )
            sheet.write(
                prod_row,
                6,
                self.float_time_convert(line.overtime_hours),
                cell_format_center,
            )
            sheet.write(
                prod_row,
                7,
                self.float_time_convert(line.absence_hours),
                cell_format_center,
            )
            sheet.write(
                prod_row,
                8,
                self.float_time_convert(line.worked_hours),
                cell_format_center,
            )
            sheet.write(
                prod_row,
                9,
                _(
                    dict(
                        line._fields["presence_state"]._description_selection(
                            self.with_context({"lang": self.env.user.lang}).env
                        )
                    ).get(line.presence_state)
                ),
                cell_format_center,
            )
            worked_hours_state = "مكتملة"
            if line.presence_state == "service" and line.absence_hours:
                worked_hours_state = "غير مكتملة"
            elif line.presence_state != "service":
                worked_hours_state = "-"
            sheet.write(
                prod_row,
                10,
                worked_hours_state,
                cell_format_center,
            )
            prod_row = prod_row + 1
        return sheet
