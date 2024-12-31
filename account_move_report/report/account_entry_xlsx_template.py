import base64
import io

from odoo import _, models

HEADER_VALS = [
    _("رقم القيد"),
    _("دفتر اليومية"),
    _("رقم الحساب"),
    _("مبلغ المدين"),
    _("مبلغ الدائن"),
    _("شرح القيد"),
    _("منشئ القيد"),
    _("التاريخ"),
    _("مراجع القيد"),
    _("التاريخ"),
    _("مؤكد القيد"),
    _("التاريخ"),
    _("معتمد القيد"),
    _("التاريخ"),
]


class AccountEntryXlsxtemplate(models.AbstractModel):
    _name = "report.account_move_report.account_entry_report_template_xlsx"
    _description = "Entries Xlsx Template"
    _inherit = "report.report_xlsx.abstract"

    def _get_entries(self, record):
        """Get entries based on dates and state"""
        date_from = record.date_from
        date_to = record.date_to
        domain = [
            ("date", "<=", date_to),
            ("date", ">=", date_from),
        ]
        if record.is_posted_entry:
            domain.append(("state", "=", "posted"))
        entries = self.env["account.move"].search(domain)
        return entries

    def generate_xlsx_report(self, workbook, data, lines):
        """Generate report xlsx."""
        docs = self.env["account.entry.report.wizard"].browse(lines.id)
        sheet = workbook.add_worksheet("Entries Report")
        if self.env.user.partner_id.lang == "ar_001":
            sheet.right_to_left()
        format_sheet = workbook.add_format(
            {
                "font_size": 12,
                "align": "center",
                "right": True,
                "left": True,
                "bottom": True,
                "top": True,
                "bold": True,
            }
        )
        format_sheet.set_align("center")
        format_sheet.set_align("vcenter")
        cell_format_center = workbook.add_format(
            {"bottom": True, "top": True, "right": True, "left": True, "font_size": 9}
        )
        cell_format_center.set_align("center")
        cell_format = workbook.add_format(
            {"bottom": True, "top": True, "right": True, "left": True, "font_size": 9}
        )
        cell_format.set_align("left")
        sheet.merge_range(
            "B1:J2",
            _("Entries Report"),
            format_sheet,
        )

        # company = self.env.user.company_id
        if self.env.user.company_id.logo:
            logo = io.BytesIO(base64.b64decode(self.env.user.company_id.logo))
            sheet.insert_image(
                "A1:B3",
                "image.png",
                {"x_scale": 0.3, "y_scale": 0.09, "image_data": logo},
            )

        prod_row = 4
        prod_col = 0
        for header_val in HEADER_VALS:
            sheet.write(prod_row, prod_col, header_val, format_sheet)
            sheet.set_column(prod_row, prod_col, 20)
            prod_col += 1
        prod_row += 1
        # get entries
        entries = self._get_entries(docs)
        for entry in entries:
            # get values for approvers, confirm user and reviewer
            reviewer_values = entry.get_approvals_details(
                "state", ("To Review", "تحت المراجعة")
            )
            confirm_values = entry.get_approvals_details(
                "state", ("Under Review", "تمت المراجعة")
            )
            approver_values = entry.get_approvals_details(
                "state", ("Confirm", "مؤكد", "تأكيد")
            )
            self.env["decimal.precision"].precision_get("Account")
            sheet.write(prod_row, 0, entry.name, cell_format_center)
            sheet.write(prod_row, 1, entry.journal_id.name, cell_format_center)
            sheet.write(
                prod_row,
                2,
                ", ".join(entry.line_ids.mapped("account_id.code")),
                cell_format_center,
            )
            sheet.write(
                prod_row, 3, sum(entry.line_ids.mapped("debit")), cell_format_center
            )
            sheet.write(
                prod_row, 4, sum(entry.line_ids.mapped("credit")), cell_format_center
            )
            sheet.write(prod_row, 5, entry.ref, cell_format_center)
            sheet.write(prod_row, 6, entry.create_uid.name, cell_format_center)
            sheet.write(
                prod_row, 7, entry.create_date.strftime("%Y-%m-%d"), cell_format_center
            )
            sheet.write(
                prod_row,
                8,
                reviewer_values["approver"] if reviewer_values else "",
                cell_format_center,
            )
            sheet.write(
                prod_row,
                9,
                reviewer_values["date"].strftime("%Y-%m-%d") if reviewer_values else "",
                cell_format_center,
            )
            sheet.write(
                prod_row,
                10,
                confirm_values["approver"] if confirm_values else "",
                cell_format_center,
            )
            sheet.write(
                prod_row,
                11,
                confirm_values["date"].strftime("%Y-%m-%d") if confirm_values else "",
                cell_format_center,
            )
            sheet.write(
                prod_row,
                12,
                approver_values["approver"] if approver_values else "",
                cell_format_center,
            )
            sheet.write(
                prod_row,
                13,
                approver_values["date"].strftime("%Y-%m-%d") if approver_values else "",
                cell_format_center,
            )
            prod_row = prod_row + 1
