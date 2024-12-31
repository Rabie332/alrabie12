import base64

from odoo import api, fields, models


class QRCodeInvoice(models.Model):
    _inherit = "account.move"

    qr_code = fields.Char("QR Code", compute="_compute_qr_code")

    @api.depends(
        "amount_total", "amount_untaxed", "invoice_date", "company_id", "company_id.vat"
    )
    def _compute_qr_code(self):
        """Generate the qr code for Saudi e-invoicing.
        Specs are available at the following link at page 23."""

        def get_qr_encoding(tag, field):
            company_name_byte_array = field.encode("UTF-8")
            company_name_tag_encoding = tag.to_bytes(length=1, byteorder="big")
            company_name_length_encoding = len(company_name_byte_array).to_bytes(
                length=1, byteorder="big"
            )
            return (
                company_name_tag_encoding
                + company_name_length_encoding
                + company_name_byte_array
            )

        for record in self:
            qr_code = ""
            if record.invoice_date and record.company_id.vat:
                seller_name_enc = get_qr_encoding(1, record.company_id.display_name)
                company_vat_enc = get_qr_encoding(2, record.company_id.vat)
                timestamp_enc = get_qr_encoding(3, str(record.invoice_date))
                invoice_total_enc = get_qr_encoding(4, str(record.amount_total))
                total_vat_enc = get_qr_encoding(
                    5,
                    str(
                        record.currency_id.round(
                            record.amount_total - record.amount_untaxed
                        )
                    ),
                )

                str_to_encode = (
                    seller_name_enc
                    + company_vat_enc
                    + timestamp_enc
                    + invoice_total_enc
                    + total_vat_enc
                )
                qr_code = base64.b64encode(str_to_encode).decode("UTF-8")
            record.qr_code = qr_code


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    tax_amount = fields.Float(string="Tax amount", compute="_compute_tax_amount")

    @api.depends("tax_ids", "price_subtotal")
    def _compute_tax_amount(self):
        for line in self:
            line.tax_amount = 0
            if line.tax_ids:
                line.tax_amount = line.price_total - line.price_subtotal
