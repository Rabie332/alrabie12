from datetime import date, datetime

from dateutil.relativedelta import relativedelta

from odoo import _, fields, models

MONTH_NAMES = {
    1: _("January"),
    2: _("February"),
    3: _("March"),
    4: _("April"),
    5: _("May"),
    6: _("June"),
    7: _("July"),
    8: _("August"),
    9: _("September"),
    10: _("October"),
    11: _("November"),
    12: _("December"),
}

HEADER_VALS = [
    _("Room Number"),
    _("Checkin MM/dd/yyyy"),
    _("Checkout MM/dd/yyyy"),
    _("Amount"),
    _("Customer Name"),
    _("Reservation Number"),
    _("Room Type"),
    _("Notes"),
]

HEADER_VALS_AR = [
    _("رقم الغرفة"),
    _("تاريخ الدخول MM/dd/yyyy"),
    _("تاريخ الخروج MM/dd/yyyy"),
    _("القيمة"),
    _("اسم العميل"),
    _("رقم الحجز"),
    _("نوع الغرفة"),
    _("ملاحظات"),
]


class HotelReservationTaxXlsxReport(models.TransientModel):
    _name = "hotel.reservation.tax.xlsx.report"
    _description = "Hotel Reservation tax Report"

    def _get_months(self):
        today = datetime.today().date()
        month_number = relativedelta(today, date(today.year, 1, 1)).months
        months = []
        for month in range(1, month_number + 1):
            months.append((month, MONTH_NAMES[month]))
        return months

    month = fields.Selection(
        "_get_months",
        "Month",
        required=1,
    )

    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, record.month))
        return result

    def print_report_xlsx(self):
        data = {"ids": [self.id], "form": self.read()[0]}
        return self.env.ref(
            "hotel_reservation_reports.reservation_tax_report_xlsx"
        ).report_action(self, data=data)


class AccountAnalyticXlsxtemplate(models.AbstractModel):
    _name = "report.hotel_reservation_reports.reservation_tax_template_xlsx"
    _description = "Hotel Reservation tax Xlsx Template"
    _inherit = "report.report_xlsx.abstract"

    def _get_reservation(self, record):
        """Get analytic based on dates and state"""
        month = record.month
        reservations = (
            self.env["hotel.reservation"]
            .search([])
            .filtered(
                lambda reservation: int(reservation.checkin.date().month) == int(month)
                and int(reservation.checkout.date().month) == int(month)
            )
        )
        return reservations

    def generate_xlsx_report(self, workbook, data, lines):
        """Generate report xlsx."""
        docs = self.env["hotel.reservation.tax.xlsx.report"].browse(lines.id)
        sheet = workbook.add_worksheet(_("Baladi Report"))
        if self.env.user.partner_id.lang == "ar_001":
            HEADER_VALS = HEADER_VALS_AR
        format_sheet = workbook.add_format(
            {
                "font_size": 12,
                "align": "center",
                "right": True,
                "left": True,
                "bottom": True,
                "top": True,
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

        prod_row = 1
        prod_col = 0
        for header_val in HEADER_VALS:
            sheet.write(prod_row, prod_col, header_val, format_sheet)
            sheet.set_column(prod_row, prod_col, 20)
            prod_col += 1
        prod_row += 1
        # get analytic
        reservations = self._get_reservation(docs)
        for reservation in reservations:
            sheet.write(
                prod_row,
                0,
                ", ".join(
                    room.name for room in reservation.reservation_line.mapped("room_id")
                ),
                format_sheet,
            )
            sheet.write(
                prod_row, 1, reservation.checkin.strftime("%m/%d/%Y"), format_sheet
            )
            sheet.write(
                prod_row, 2, reservation.checkout.strftime("%m/%d/%Y"), format_sheet
            )

            sheet.write(
                prod_row, 3, reservation.hotel_invoice_id.amount_untaxed, format_sheet
            )
            sheet.write(prod_row, 4, reservation.partner_id.name, format_sheet)
            sheet.write(prod_row, 5, reservation.reservation_no, format_sheet)
            sheet.write(
                prod_row,
                6,
                ", ".join(
                    room.room_categ_id.name
                    for room in reservation.reservation_line.mapped("room_id")
                ),
                format_sheet,
            )
            sheet.write(prod_row, 7, "", format_sheet)
            prod_row += 1
