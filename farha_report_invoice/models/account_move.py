from ummalqura.hijri_date import HijriDate

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    def get_hijri_date(self, georging_date, separator):
        """Convert georging date to hijri date.

        :return hijri date as a string value
        """
        if georging_date:
            georging_date = fields.Date.from_string(georging_date)
            hijri_date = HijriDate(
                georging_date.year, georging_date.month, georging_date.day, gr=True
            )
            return (
                str(int(hijri_date.year)).zfill(2)
                + separator
                + str(int(hijri_date.month)).zfill(2)
                + separator
                + str(int(hijri_date.day))
            )
        return None

    def get_amount_to_text(self, amount):
        """Get amount to words."""
        self.ensure_one()
        if amount:
            amount_text = self.currency_id.amount_to_text(amount)
            amount_text = amount_text.replace("مائة", "مائة و ")
            amount_text = amount_text.replace("مئتان", "مئتان و ")
            amount_text = amount_text.replace("ثلاثمائة", "ثلاثمائة و ")
            amount_text = amount_text.replace("أربعمائة", "أربعمائة و ")
            amount_text = amount_text.replace("خمسمائة", "خمسمائة و ")
            amount_text = amount_text.replace("ستمائة", "ستمائة و ")
            amount_text = amount_text.replace("سبعمائة", "سبعمائة و ")
            amount_text = amount_text.replace("ثمانمائة", "ثمانمائة و ")
            amount_text = amount_text.replace("تسعمائة", "تسعمائة و ")
            amount_text = (
                amount_text.replace("  ", " ").replace(",", " و").replace("،", " و")
            )
            amount_text = amount_text.replace("and", "و")
            amount_text = amount_text.replace("عشرين", "عشرون")
            amount_text = amount_text.replace("ثلاثين", "ثلاثون")
            amount_text = amount_text.replace("أربعين", "أربعون")
            amount_text = amount_text.replace("خمسين", "خمسون")
            amount_text = amount_text.replace("ستين", "ستون")
            amount_text = amount_text.replace("سبعين", "سبعون")
            amount_text = amount_text.replace("ثمانين", "ثمانون")
            amount_text = amount_text.replace("تسعين", "تسعون")
            amount_text = amount_text.replace("Riyal", "ريال")
            return amount_text
        return True

    def print_report_clearance_invoice(self):
        return self.env.ref(
            "farha_report_invoice.account_move_clearance_report"
        ).report_action(self)

    def get_approvals_details(self, new_value_char):
        # filter messages per stage
        for move in self:
            track_obj = move.env["mail.tracking.value"]
            ir_model = self.env["ir.model"].sudo().search([("model", "=", move._name)])
            ir_model_field = (
                move.env["ir.model.fields"]
                .sudo()
                .search([("model_id", "=", ir_model.id), ("name", "=", "state")])
            )
            tracking_line = track_obj.sudo().search(
                [
                    ("mail_message_id.res_id", "=", move.id),
                    ("mail_message_id.model", "=", move._name),
                    ("field", "=", ir_model_field.id),
                    ("new_value_char", "in", new_value_char),
                ],
                limit=1,
            )
            values = ""
            if tracking_line:
                values = tracking_line.create_uid.employee_id.name
            return values


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    tax_amount = fields.Float(string="Tax amount", compute="_compute_tax_amount")

    @api.depends("tax_ids", "price_subtotal")
    def _compute_tax_amount(self):
        for line in self:
            line.tax_amount = 0
            if line.tax_ids:
                line.tax_amount = line.price_total - line.price_subtotal
