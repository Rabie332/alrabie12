from odoo import _, fields, models

HEADER_VALS = [
    "Employee # \n الرقم الوظيفى",
    "Employee Name \n إسم الموظف",
    "Account # \n رقم الحساب",
    "Bank \n البنك",
    "Payment Method \n طريقة الصرف",
    "Amount \n المبلغ",
    "Legal # \n رقم الهوية/الاقامة",
    "Employee Basic Wage # \n الراتب الاساسى ",
    "Housing Allowance \n بدل السكن",
    "Other Earnings \n دخل اخر",
    "Deductions \n الخصومات",
]


class PayslipRunBankXls(models.AbstractModel):
    _name = "report.farha_custom.report_payslip_run_bank_xlsx"
    _inherit = "report.report_xlsx.abstract"
    _description = "Payslip Run Bank Report Excel"

    def generate_xlsx_report(self, workbook, data, lines):
        """Generate report xlsx."""
        docs = self.env["hr.payslip.run"].browse(lines.id)
        sheet = workbook.add_worksheet(_("Payroll submitted to the bank"))
        font_size_8 = workbook.add_format(
            {"bottom": True, "top": True, "right": True, "left": True, "font_size": 12}
        )
        font_size_8.set_align("center")
        bank_account = ""
        mol_establishment = ""
        sheet.set_column("A:F", 20)

        # Create a format to use in the merged range.
        merge_format = workbook.add_format(
            {
                "bold": 1,
                "border": 1,
                "align": "center",
                "color": "#FFFFFF",
                "valign": "vcenter",
            }
        )
        merge_format.set_bg_color("#4f81bd")
        format_header = workbook.add_format(
            {"bold": 1, "border": 1, "align": "center", "valign": "vcenter"}
        )
        format_header.set_bg_color("#64b4ff")
        format_header_text = workbook.add_format(
            {"bold": 1, "border": 1, "align": "center", "valign": "vcenter"}
        )

        # # Merge 3 cells over two rows.
        sheet.merge_range("A1:F2", "", format_header)
        sheet.insert_image(
            "A1:B1",
            "/farha_custom/static/src/img/bank.png",
            {"x_scale": 1.5, "y_scale": 1.5},
        )
        sheet.merge_range("A3:A4", "Corporate Name \n إسم الشركة", merge_format)
        sheet.merge_range("B3:B4", docs.company_id.name, format_header_text)
        sheet.merge_range("A5:A6", "Account # \n رقم الحساب", merge_format)
        if len(docs.company_id.partner_id.bank_ids) != 0:
            bank_account = docs.company_id.partner_id.bank_ids[0].acc_number
        sheet.merge_range("B5:B6", bank_account, format_header_text)
        sheet.merge_range("A7:A8", "CIF \n رقم الملف", merge_format)
        sheet.merge_range("B7:B8", docs.name, format_header_text)

        sheet.merge_range("C3:C4", "Type \n النوع", merge_format)
        sheet.merge_range("D3:D4", "WPS", format_header_text)
        sheet.merge_range("C5:C6", "Date \n التاريخ", merge_format)
        sheet.merge_range(
            "D5:D6", fields.Date.today().strftime("%Y-%m-%d"), format_header_text
        )
        sheet.merge_range("C7:C8", "Due Date \n تاريخ الإستحقاق", merge_format)
        sheet.merge_range(
            "D7:D8", docs.date_end.strftime("%Y-%m-%d"), format_header_text
        )
        sheet.set_row(3, 20)
        sheet.merge_range("E3:E4", "Trx Count \n إجمالى العمليات", merge_format)
        sheet.merge_range("F3:F4", len(docs.slip_ids), format_header_text)
        sheet.merge_range("E5:E6", "Total Salaries \n إجمالى الرواتب", merge_format)
        sheet.merge_range(
            "F5:F6", sum(docs.slip_ids.mapped("total_payslip")), format_header_text
        )
        sheet.merge_range(
            "E7:E8", "MOL Establishment ID: \n رقم مكتب العمل", merge_format
        )
        if docs.company_id and docs.company_id.mol_establishment:
            mol_establishment = docs.company_id.mol_establishment
        sheet.merge_range("F7:F8", mol_establishment, format_header_text)
        sheet.set_row(7, 20)
        prod_row = 9
        # Set header
        prod_col = 0
        for header_val in HEADER_VALS:
            sheet.write(prod_row, prod_col, header_val, merge_format)
            sheet.set_column(prod_row, prod_col, len(header_val))
            sheet.set_row(prod_row, 50)
            prod_col += 1
        prod_row += 1
        # set lines
        for line in docs.slip_ids:
            account_employee = ""
            bank = ""
            identification_residence = ""
            number = ""
            if line.employee_id.number:
                number = line.employee_id.number
            sheet.write(prod_row, 0, number, font_size_8)
            sheet.write(prod_row, 1, line.employee_id.name, font_size_8)
            if line.employee_id and line.employee_id.bank_account_id:
                account_employee = line.employee_id.bank_account_id.acc_number
                if line.employee_id.bank_account_id.bank_id:
                    bank = line.employee_id.bank_account_id.bank_id.name
            sheet.write(prod_row, 2, account_employee, font_size_8)
            sheet.write(prod_row, 3, bank, font_size_8)
            sheet.write(prod_row, 4, "BANK ACCOUNT", font_size_8)
            # sheet.write(prod_row, 5, line.total_payslip, font_size_8)
            if line.employee_id.identification_id:
                identification_residence = line.employee_id.identification_id
            if line.employee_id.residence_id:
                identification_residence = line.employee_id.residence_id
            sheet.write(prod_row, 6, identification_residence, font_size_8)
            basic = sum(
                line_slip.total
                for line_slip in line.line_ids
                if line_slip.category_id == line.env.ref("hr_payroll.BASIC")
            )
            ALWH = sum(
                line_slip.total
                for line_slip in line.line_ids
                if line_slip.code == "ALWH"
            )
            ALWO = sum(
                line_slip.total
                for line_slip in line.line_ids
                if line_slip.code == "ALWO"
            )
            GOSI = sum(
                line_slip.total
                for line_slip in line.line_ids
                if line_slip.code == "GOSI"
            )
            # Compute the total payslip amount as the sum of the above components
            total_payslip_amount = line.contract_id.wage_net
            allowances_total = line.contract_id.total_bonus
            social_insurance = line.contract_id.social_insurance
            housing_allowance = line.contract_id.housing_allowance
            wage = line.contract_id.wage

            # Write the computed total to the sheet
            sheet.write(prod_row, 5, total_payslip_amount, font_size_8)
            sheet.write(prod_row, 7, wage, font_size_8)
            sheet.write(prod_row, 8, allowances_total, font_size_8)
            sheet.write(prod_row, 9, housing_allowance, font_size_8)
            sheet.write(prod_row, 10, social_insurance, font_size_8)

            prod_row = prod_row + 1
