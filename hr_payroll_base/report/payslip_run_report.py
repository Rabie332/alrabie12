from odoo import _, models

HEADER_VALS = [
    "المرجع",
    "الموظف",
    "الفترة",
    "التاريخ من",
    "التاريخ إلى",
    "الصافي",
    "الحالة",
]


class PayslipRunXls(models.AbstractModel):
    _name = "report.hr_payroll_base.report_payslip_run_xlsx"
    _inherit = "report.report_xlsx.abstract"
    _description = "Payslip Run Report Excel"

    def generate_xlsx_report(self, workbook, data, lines):
        """Generate report xlsx."""
        docs = self.env["hr.payslip.run"].browse(lines.id)
        categories = "الوسوم : "
        sheet = workbook.add_worksheet(_("مسيرات الرواتب"))
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
            {"bottom": True, "top": True, "right": True, "left": True, "font_size": 12}
        )
        font_size_8.set_align("center")
        sheet.merge_range(
            "A1:G1",
            _("مسير الرواتب {} : من {} إلى {}").format(
                docs.name, docs.date_start, docs.date_end
            ),
            format_sheet1,
        )
        if docs.category_ids:
            for category in docs.category_ids:
                categories += category.name
                if category.id != docs.category_ids[-1].id:
                    categories += ", "
        sheet.merge_range("A2:G2", _(categories), format_sheet1)
        sheet.merge_range(
            "A3:G3", _("الإجمالي : {} ريال").format(docs.total_slips), format_sheet1
        )
        prod_row = 3
        prod_row = prod_row + 1
        # Set header
        prod_col = 0
        for header_val in HEADER_VALS:
            sheet.write(prod_row, prod_col, header_val, format_sheet)
            sheet.set_column(prod_row, prod_col, len(header_val) * 4)
            prod_col += 1
        prod_row += 1
        # set lines
        for line in docs.slip_ids:
            sheet.write(prod_row, 0, line.number, font_size_8)
            sheet.write(prod_row, 1, line.employee_id.name, font_size_8)
            sheet.write(prod_row, 2, line.hr_period_id.name, font_size_8)
            sheet.write(prod_row, 3, str(line.date_from), font_size_8)
            sheet.write(prod_row, 4, str(line.date_to), font_size_8)
            sheet.write(prod_row, 5, line.total_payslip, font_size_8)
            if line.state == "draft":
                sheet.write(prod_row, 6, _("مسودة"), font_size_8)
            elif line.state == "verify":
                sheet.write(prod_row, 6, _("جاري الانتظار"), font_size_8)
            elif line.state == "done":
                sheet.write(prod_row, 6, _("تم"), font_size_8)
            else:
                sheet.write(prod_row, 6, _("مرفوض"), font_size_8)
            prod_row = prod_row + 1
