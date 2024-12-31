import base64
import io

from odoo import _, models


class SalaryHistoryReportXlsxTemplate(models.AbstractModel):
    _name = "report.hr_salary_request.salary_history_template_xlsx"
    _inherit = "report.report_xlsx.abstract"
    _description = "History Salary Report Xlsx Template"

    def _get_name(self, code):
        name = self.env["hr.salary.rule"].search([("code", "=", code)]).mapped("name")
        if name:
            return name[0]
        else:
            return ""

    def _get_header(self, record):
        header_vals = []
        payslips = (
            record.env["hr.payslip"]
            .sudo()
            .search([("employee_id", "=", record.employee_id.id)])
        )
        for payslip in payslips:
            payslip_lines = (
                self.env["hr.payslip.line"]
                .search([("slip_id", "=", payslip.id)])
                .mapped("code")
            )
            for line in payslip_lines:
                if line not in header_vals:
                    header_vals.append(line)
        if "NET" in header_vals:
            header_vals.remove("NET")
        return header_vals

    def get_column(self, lines, header):
        columns = []
        payslips = (
            lines.env["hr.payslip"]
            .sudo()
            .search(
                [
                    ("employee_id", "=", lines.employee_id.id),
                    ("date_to", "<", lines.date),
                ],
                order="id desc",
                limit=3,
            )
        )
        for payslip in payslips:
            col = (
                self.env["hr.payslip.line"]
                .search([("slip_id", "=", payslip.id), ("code", "=", header)])
                .mapped("total")
            )
            columns.append(col)
        return columns

    def get_months(self, lines):
        months = (
            lines.env["hr.payslip"]
            .sudo()
            .search(
                [
                    ("employee_id", "=", lines.employee_id.id),
                    ("date_to", "<", lines.date),
                ],
                order="id desc",
                limit=3,
            )
            .mapped("date_to")
        )
        return months

    def generate_xlsx_report(self, workbook, data, lines):
        """Generate report xlsx."""
        self = self.with_context(lang=self.env.user.lang)
        sheet = workbook.add_worksheet("كشف راتب")
        sheet.right_to_left()
        cell_format_header = workbook.add_format(
            {
                "align": "center",
                "bottom": True,
                "top": True,
                "right": True,
                "left": True,
                "font_size": 12,
            }
        )

        cell_format_header_bleu = workbook.add_format(
            {
                "bg_color": "#9DC3E6",
                "align": "center",
                "bottom": True,
                "top": True,
                "right": True,
                "left": True,
                "font_size": 12,
            }
        )

        cell_format_title_bleu = workbook.add_format(
            {
                "bg_color": "#BDD7EE",
                "align": "center",
                "bottom": True,
                "top": True,
                "right": True,
                "left": True,
                "font_size": 12,
            }
        )

        cell_format_red = workbook.add_format(
            {
                "align": "center",
                "bottom": True,
                "top": True,
                "right": True,
                "left": True,
                "color": "red",
                "font_size": 12,
            }
        )

        sheet.merge_range(
            "A1:B1",
            lines.company_id.name,
            cell_format_red,
        )
        if lines.company_id.vat:
            sheet.merge_range(
                "A2:B2",
                _("شركة ذات مسئولية محدودة س ت {}").format(lines.company_id.vat),
                cell_format_header,
            )
        else:
            sheet.merge_range("A2:B2", "شركة ذات مسئولية محدودة", cell_format_header)
        if lines.company_id.country_id:
            sheet.merge_range(
                "A3:B3", lines.company_id.country_id.name, cell_format_header
            )
        else:
            sheet.merge_range("A3:B3", "", cell_format_header)

        if lines.company_id.street:
            sheet.merge_range("A4:B4", lines.company_id.street, cell_format_header)
        else:
            sheet.merge_range("A4:B4", "", cell_format_header)
        if lines.company_id.zip:
            sheet.merge_range(
                "A5:B5",
                _("الرمز البريدي {}").format(lines.company_id.zip),
                cell_format_header,
            )
        else:
            sheet.merge_range("A5:B5", "", cell_format_header)
        if lines.company_id.phone and lines.company_id.fax:
            sheet.merge_range(
                "A6:B6",
                _("هاتف: {} | فاكس: {}").format(
                    lines.company_id.phone, lines.company_id.fax
                ),
                cell_format_header,
            )
        elif lines.company_id.phone:
            sheet.merge_range(
                "A6:B6",
                _("هاتف: {}").format(lines.company_id.phone),
                cell_format_header,
            )
        elif lines.company_id.fax:
            sheet.merge_range(
                "A6:B6",
                _("فاكس: {}").format(lines.company_id.fax),
                cell_format_header,
            )
        else:
            sheet.merge_range("A6:B6", "", cell_format_header)

        if lines.company_id.logo:
            logo = io.BytesIO(base64.b64decode(lines.company_id.logo))
            sheet.insert_image(
                "M1:P6",
                "image.png",
                {"x_scale": 0.5, "y_scale": 0.5, "image_data": logo},
            )
        sheet.merge_range(
            "A8:Q8",
            _("مسير رواتب شركة {}").format(lines.company_id.name),
            cell_format_header_bleu,
        )

        prod_row = 8
        col = 0
        sheet.set_column(prod_row, col, 20)
        header_vals = self._get_header(lines)
        sheet.write(prod_row, col, "الموظف", cell_format_title_bleu)
        sheet.write(prod_row, col + 1, "الشهر", cell_format_title_bleu)
        col = 1
        for header in header_vals:
            sheet.set_column(prod_row, col, 20)
            col += 1
            sheet.write(prod_row, col, self._get_name(header), cell_format_title_bleu)
        col += 1
        sheet.write(prod_row, col, "الغياب و التأخير", cell_format_title_bleu)
        sheet.write(prod_row, col + 1, self._get_name("NET"), cell_format_title_bleu)
        rows = self.get_column(lines, "NET")
        for line in rows:
            prod_row += 1
            sheet.set_column(prod_row, col + 1, 20)
            sheet.write_row(prod_row, col + 1, line, cell_format_header)
        col = 1
        for header in header_vals:
            prod_row = 8
            col += 1
            rows = self.get_column(lines, header)
            for line in rows:
                prod_row += 1
                sheet.write_row(prod_row, col, line, cell_format_header)
        prod_row = 8
        col = 1
        months = self.get_months(lines)
        for month in months:
            prod_row += 1
            sheet.write(prod_row, col - 1, lines.employee_id.name, cell_format_header)
            sheet.write(prod_row, col, month.strftime("%Y/%m"), cell_format_header)

        prod_row += 3
        col = 2
        sheet.write(prod_row, col, "الموارد البشرية", cell_format_header)
        col += 4
        sheet.write(prod_row, col, "الإدارة المالية", cell_format_header)
        col += 4
        sheet.write(prod_row, col, "الرئيس التنفيذي", cell_format_header)
