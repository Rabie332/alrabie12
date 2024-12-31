import math

from odoo import _, fields, models

HEADER_VALS1 = [
    "",
    "رقم المعاملة",
    "المرجع",
    "رقم بوليصة الشحن",
    "الكمية",
    "رقم البيان",
    "تاريخ التسليم في البضاعة ",
    "تاريخ سحب البضاعه من الميناء ",
    "تاريخ توصيل البضاعه ",
    "تاريخ ارجاع الفارغ للوكيل الملاحي",
    "تاريخ ارسال الفاتورة للعميل ",
    "حالة المعاملة ",
]
HEADER_VALS2 = [
    "S.N",
    "Job No",
    "PO",
    "B / L",
    "Quantity",
    "Bayan",
    "Schedule Delivery Date",
    "Pull Out Date",
    "Actual Delivery Date",
    "Return the empty container",
    "Last Date for Return the Containers",
    "State",
]


class ClearanceRequestXls(models.AbstractModel):
    _name = "report.clearance.clearance_request_xlsx"
    _inherit = "report.report_xlsx.abstract"
    _description = "Clearance Reports XLS"

    def float_time_convert(self, float_val):
        factor = float_val < 0 and -1 or 1
        val = abs(float_val)
        hour, minute = (factor * int(math.floor(val)), int(round((val % 1) * 60)))
        if minute == 60:
            hour = hour + 1
            minute = 0
        return "{:02d}:{:02d}".format(hour, minute)

    def _get_lines(self, record):
        domain = []
        if record.date_from:
            domain = [("date", ">=", record.date_from)]
        if record.date_to:
            domain.append(("date", "<=", record.date_to))
        if record.state:
            domain.append(("state", "=", record.state))
        if record.partner_id:
            domain.append(("partner_id", "=", record.partner_id.id))
        clearance_ids = self.env["clearance.request"].search(domain, order="id desc")
        return clearance_ids

    def generate_xlsx_report(self, workbook, data, lines):  # noqa: C901
        """Generate report xlsx."""
        docs = self.env["clearance.request.wizard"].browse(lines.id)
        date_from = docs.date_from
        date_to = docs.date_to
        sheet = workbook.add_worksheet("DELIVERY REPORT")
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
            "A1:L2",
            "تقرير طلبات التخليص : من  {} إلى {}".format(date_from, date_to),
            format_sheet1,
        )
        sheet.merge_range(
            "A3:L4",
            ("DELIVERY REPORT: from  %s to %s") % (date_from, date_to),
            format_sheet1,
        )
        # Set header
        prod_row = 5
        prod_col = 0
        for header_val in HEADER_VALS1:
            sheet.write(prod_row, prod_col, header_val, format_sheet)
            sheet.set_column(prod_row, prod_col, len(header_val) * 2)
            prod_col += 1
        prod_row += 1
        prod_col = 0
        for header in HEADER_VALS2:
            sheet.write(prod_row, prod_col, header, format_sheet)
            prod_col += 1
        prod_row += 1
        # set lines
        lines = self._get_lines(docs)
        for line in lines:
            sheet.write(prod_row, 0, line.name, cell_format_center)
            sheet.write(prod_row, 1, line.name, cell_format_center)
            sheet.write(
                prod_row,
                2,
                line.reference if line.reference else "-",
                cell_format_center,
            )
            sheet.write(
                prod_row,
                3,
                line.shipping_number if line.shipping_number else "-",
                cell_format_center,
            )
            shipment_text = "-"
            for shipment in line.shipment_type_line_ids:
                shipment_type = " "
                if shipment.shipment_type_size_id.name and line.number_shipment:
                    shipment_type = (
                        str(line.number_shipment)
                        + str("X")
                        + str(shipment.shipment_type_size_id.name)
                    )
                shipment_text += shipment_type + str("  ")
            sheet.write(prod_row, 4, shipment_text, cell_format_center)

            sheet.write(
                prod_row,
                5,
                line.statement_number if line.statement_number else "-",
                cell_format_center,
            )
            delivery_date = "-"
            if line.order_ids and line.order_ids[-1].line_ids:
                delivery_date = " "
                for order in line.order_ids[-1].line_ids:
                    delivery_date += str(order.delivery_date) + str("//")
            sheet.write(
                prod_row,
                6,
                delivery_date,
                cell_format_center,
            )

            sheet.write(
                prod_row,
                7,
                line.order_ids[0].create_date.strftime("%Y-%m-%d")
                if line.order_ids
                else "-",
                cell_format_center,
            )
            sheet.write(
                prod_row,
                8,
                str(line.date_receipt) if line.date_receipt else "-",
                cell_format_center,
            )
            sheet.write(
                prod_row,
                9,
                str(line.last_date_empty_container)
                if line.last_date_empty_container
                else "-",
                cell_format_center,
            )
            sheet.write(
                prod_row,
                10,
                str(line.account_move_ids[0].invoice_date)
                if line.account_move_ids and line.account_move_ids[0].invoice_date
                else "-",
                cell_format_center,
            )
            if line.state == "draft":
                sheet.write(prod_row, 11, "مسودة", cell_format_center)
            elif line.state == "customs_clearance":
                sheet.write(prod_row, 11, "التخليص الجمركي", cell_format_center)
            elif line.state == "customs_statement":
                sheet.write(prod_row, 11, "البيان الجمركي", cell_format_center)
            elif line.state == "transport":
                sheet.write(prod_row, 11, "نقل", cell_format_center)
            elif line.state == "delivery":
                sheet.write(prod_row, 11, "استلام و توصيل", cell_format_center)
            elif line.state == "delivery_done":
                sheet.write(prod_row, 11, "تم التسليم", cell_format_center)
            elif line.state == "close":
                sheet.write(prod_row, 11, "إقفال", cell_format_center)
            else:
                sheet.write(prod_row, 11, _("ملغي"), cell_format_center)
            prod_row = prod_row + 1
        return sheet


class ClearanceRequestPartnertXls(models.AbstractModel):
    _name = "report.clearance.clearance_request_partner_xlsx"
    _inherit = "report.report_xlsx.abstract"
    _description = "Clearance Reports XLS"

    def float_time_convert(self, float_val):
        factor = float_val < 0 and -1 or 1
        val = abs(float_val)
        hour, minute = (factor * int(math.floor(val)), int(round((val % 1) * 60)))
        if minute == 60:
            hour = hour + 1
            minute = 0
        return "{:02d}:{:02d}".format(hour, minute)

    def _get_lines(self, partner_id):
        today = fields.Date.today()
        clearance_obj = self.env["clearance.request"]
        domain = [("state", "!=", "delivery_done"), ("partner_id", "=", partner_id)]
        domain_today = [("date_receipt", "=", today), ("state", "=", "delivery_done")]
        clearance_requests = clearance_obj.search(domain, order="id desc")
        clearance_requests_today = clearance_obj.search(domain_today, order="id desc")
        clearance_requests = clearance_requests + clearance_requests_today
        return clearance_requests

    def generate_xlsx_report(self, workbook, data, lines):  # noqa: C901
        """Generate report xlsx."""
        docs = self.env["res.partner"].browse(lines.id)
        sheet = workbook.add_worksheet("DELIVERY REPORT")
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
            "A1:L2",
            "تقرير طلبات التخليص ",
            format_sheet1,
        )
        sheet.merge_range(
            "A3:L4",
            ("DELIVERY REPORT"),
            format_sheet1,
        )
        # Set header
        prod_row = 5
        prod_col = 0
        for header_val in HEADER_VALS1:
            sheet.write(prod_row, prod_col, header_val, format_sheet)
            sheet.set_column(prod_row, prod_col, len(header_val) * 2)
            prod_col += 1
        prod_row += 1
        prod_col = 0
        for header in HEADER_VALS2:
            sheet.write(prod_row, prod_col, header, format_sheet)
            prod_col += 1
        prod_row += 1
        # set lines
        lines = self._get_lines(docs.id)
        for line in lines:
            sheet.write(prod_row, 0, line.name, cell_format_center)
            sheet.write(prod_row, 1, line.name, cell_format_center)
            sheet.write(
                prod_row,
                2,
                line.reference if line.reference else "-",
                cell_format_center,
            )
            sheet.write(
                prod_row,
                3,
                line.shipping_number if line.shipping_number else "-",
                cell_format_center,
            )
            sheet.write(
                prod_row,
                4,
                line.number_shipment if line.number_shipment else "-",
                cell_format_center,
            )
            sheet.write(
                prod_row,
                5,
                line.statement_number if line.statement_number else "-",
                cell_format_center,
            )
            sheet.write(
                prod_row,
                6,
                line.statement_line_ids[0].delivery_date
                if line.statement_line_ids and line.statement_line_ids[0].delivery_date
                else "-",
                cell_format_center,
            )
            sheet.write(
                prod_row,
                7,
                line.order_ids[0].create_date.strftime("%Y-%m-%d")
                if line.order_ids
                else "-",
                cell_format_center,
            )
            sheet.write(
                prod_row,
                8,
                str(line.date_receipt) if line.date_receipt else "-",
                cell_format_center,
            )
            sheet.write(
                prod_row,
                9,
                str(line.last_date_empty_container)
                if line.last_date_empty_container
                else "-",
                cell_format_center,
            )
            sheet.write(
                prod_row,
                10,
                str(line.account_move_ids[0].invoice_date)
                if line.account_move_ids and line.account_move_ids[0].invoice_date
                else "-",
                cell_format_center,
            )
            if line.state == "draft":
                sheet.write(prod_row, 11, "مسودة", cell_format_center)
            elif line.state == "customs_clearance":
                sheet.write(prod_row, 11, "التخليص الجمركي", cell_format_center)
            elif line.state == "customs_statement":
                sheet.write(prod_row, 11, "البيان الجمركي", cell_format_center)
            elif line.state == "transport":
                sheet.write(prod_row, 11, "نقل", cell_format_center)
            elif line.state == "delivery":
                sheet.write(prod_row, 11, "استلام و توصيل", cell_format_center)
            elif line.state == "delivery_done":
                sheet.write(prod_row, 11, "تم التسليم", cell_format_center)
            elif line.state == "close":
                sheet.write(prod_row, 11, "إقفال", cell_format_center)
            else:
                sheet.write(prod_row, 11, _("ملغي"), cell_format_center)
            prod_row = prod_row + 1
        return sheet
