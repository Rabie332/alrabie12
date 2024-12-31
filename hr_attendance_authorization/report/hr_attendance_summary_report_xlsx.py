from odoo import _, models


class AttendanceSummaryReportXls(models.AbstractModel):
    _inherit = "report.hr_attendance_summary.report_attendance_summary_xlsx"

    def generate_xlsx_report(self, workbook, data, lines):
        """Generate report xlsx."""
        sheet = super(AttendanceSummaryReportXls, self).generate_xlsx_report(
            workbook, data, lines
        )
        docs = self.env["hr.attendance.report"].browse(lines.id)
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
        format_sheet.set_bg_color("#395870")
        cell_format_center = workbook.add_format(
            {"bottom": True, "top": True, "right": True, "left": True, "font_size": 10}
        )
        cell_format_center.set_align("center")
        sheet.write(2, 9, "إستئذان", format_sheet)
        sheet.write(2, 10, "حالة الحضور", format_sheet)
        sheet.set_column(2, 10, 20)
        prod_row = 3
        lines = self._get_lines(docs)
        # calculate authorization_hours in attendance report xls
        for line in lines:
            sheet.write(
                prod_row,
                9,
                self.float_time_convert(line.authorization_hours),
                cell_format_center,
            )
            sheet.write(
                prod_row,
                10,
                _(
                    dict(
                        line._fields["presence_state"]._description_selection(
                            self.with_context({"lang": self.env.user.lang}).env
                        )
                    ).get(line.presence_state)
                ),
                cell_format_center,
            )
            prod_row = prod_row + 1
