from odoo import models

HEADER_VALS = [
    "رقم الطلب",
    "الموظف",
    "الرقم الوظيفي",
    "الادارة",
    "التاريخ",
    "النوع",
    "الوصف",
    "المرحلة",
    "الإسترجاع",
]


class HrCovenantReportXls(models.AbstractModel):
    _name = "report.hr_covenant.report_hr_covenant_resume_xlsx"
    _inherit = "report.report_xlsx.abstract"
    _description = "Hr Covenant Resume Reports XLS"

    def _get_covenants(self, record):
        """Get covenants from hr.covenant model."""
        date_from = record.date_from
        date_to = record.date_to
        department_id = record.department_id.id or False
        employee_id = record.employee_id.id or False
        retrieval = record.retrieval
        domain = [
            ("date", ">=", date_from),
            ("date", "<=", date_to),
        ]
        if department_id:
            domain += [("department_id", "=", department_id)]
        if employee_id:
            domain += [("employee_id", "=", employee_id)]
        if retrieval:
            domain += [("retrieval", "=", retrieval)]
        return self.env["hr.covenant"].search(domain)

    def generate_xlsx_report(self, workbook, data, lines):
        """Generate report xlsx."""
        self = self.with_context(lang=self.env.user.lang)
        docs = self.env["hr.covenant.wizard"].browse(lines.ids)
        date_from = docs.date_from
        date_to = docs.date_to
        sheet = workbook.add_worksheet("تقرير حصر العهد")
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
            "A1:I2",
            "تقرير حصر العهد: من  %s إلى %s" % (date_from, date_to),
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
        # set lines
        covenants = self._get_covenants(docs)
        for covenant in covenants:
            sheet.write(prod_row, 0, covenant.name, font_size_8)
            if covenant.employee_id.number:

                sheet.write(prod_row, 1, covenant.employee_id.number, font_size_8)
            else:
                sheet.write(prod_row, 1, "-", font_size_8)
            sheet.write(prod_row, 2, covenant.employee_id.name, font_size_8)
            sheet.write(
                prod_row,
                3,
                covenant.employee_id.department_id.name,
                font_size_8,
            )
            sheet.write(prod_row, 4, covenant.date.strftime("%Y-%m-%d"), font_size_8)
            sheet.write(prod_row, 5, covenant.covenant_type_id.name, font_size_8)
            if covenant.description:
                sheet.write(prod_row, 6, covenant.description, font_size_8)
            else:
                sheet.write(prod_row, 6, "", font_size_8)
            sheet.write(prod_row, 7, covenant.stage_id.name, font_size_8)
            if covenant.retrieval:
                sheet.write(prod_row, 8, "تم الإسترجاع", font_size_8)
            else:
                sheet.write(prod_row, 8, "عند الموظف", font_size_8)
            prod_row += 1
