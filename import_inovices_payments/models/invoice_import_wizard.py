import base64
import xlrd
import json
import time
from datetime import datetime
from odoo.exceptions import UserError
from odoo import models, fields, api, _
import logging
import hashlib

_logger = logging.getLogger(__name__)


class InvoiceImportWizard(models.TransientModel):
    _name = 'invoice.import.wizard'
    _description = 'Invoice Import Wizard'

    wizard_desc = fields.Char(
        string="Excel Format", default="Excel format must be in this order: 'Customer Name', 'Invoice Date', 'Invoice Label', 'Amount with taxes', 'Product'", readonly=True)
    file = fields.Binary('File', required=True)

    company = fields.Many2one(
        'res.company', required=True, string='Invoice Company')

    journal = fields.Many2one(
        'account.journal', required=True, string='Invoice Journal')

    taxes = fields.Many2many(
        'account.tax', string='Invoice Taxes')

    def import_file(self):
        if not self.file:
            raise UserError(_("Please upload a file to import."))

        file_data = base64.b64decode(self.file)
        encoded_file_data = base64.b64encode(file_data).decode('utf-8')
        self.with_delay().process_file(encoded_file_data)

    @api.model
    def process_file(self, encoded_file_data):
        _logger.info('Start processing invoice file')
        file_data = base64.b64decode(encoded_file_data.encode('utf-8'))
        workbook = xlrd.open_workbook(file_contents=file_data)
        sheet = workbook.sheet_by_index(0)

        partner_cache = {}
        failed_rows = []

        for row in range(1, sheet.nrows):
            try:
                _logger.info(f"Processing row {row}: {sheet.row_values(row)}")
                _logger.info(
                    f"Row types: {[type(sheet.cell_value(row, col)) for col in range(sheet.ncols)]}")

                partner_name = str(sheet.cell_value(row, 0))
                invoice_date = xlrd.xldate.xldate_as_datetime(
                    sheet.cell_value(row, 1), workbook.datemode)
                label = str(sheet.cell_value(row, 2))
                net_value = float(sheet.cell_value(row, 3))
                product_name = str(sheet.cell_value(row, 4))

                product = self.env['product.product'].search(
                    [('name', '=', product_name), ('company_id', '=', self.company.id)], limit=1)

                if not product:
                    product = self.env['product.product'].create({
                        'name': product_name,
                        'company_id': self.company.id
                    })

                # Ensure numeric types are floats
                if isinstance(net_value, str):
                    net_value = float(net_value)

                # Check for proper numeric conversion
                if not isinstance(net_value, (int, float)):
                    raise ValueError(
                        f"Invalid net_value type: {type(net_value)} - value: {net_value}")

                _logger.info(
                    f"Parsed values - Partner: {partner_name}, Date: {invoice_date}, Label: {label}, Net Value: {net_value}")

                if partner_name in partner_cache:
                    partner = partner_cache[partner_name]
                else:
                    partner = self.env['res.partner'].sudo().search(
                        [('name', '=', partner_name), ('company_id', '=', self.company.id)], limit=1)
                    if not partner:
                        partner = self.env['res.partner'].sudo().create({
                            'name': partner_name,
                            'company_id': self.company.id,
                        })
                    partner_cache[partner_name] = partner

                invoice_line_vals = {
                    'product_id': product.id,
                    'name': label,
                    'quantity': 1.00,
                    'price_unit': net_value,
                    'tax_ids': [(6, 0, self.taxes.ids)],
                }

                invoice_vals = {
                    'partner_id': partner.id,
                    'invoice_date': invoice_date.isoformat(),
                    'journal_id': self.journal.id,
                    'move_type': 'out_invoice',
                    'invoice_line_ids': [(0, 0, invoice_line_vals)],
                    'company_id': self.company.id,
                }
                self.create_single_invoice(invoice_vals)
            except Exception as e:
                failed_rows.append((row, str(e)))
                _logger.error(f"Failed to process row {row}: {e}")
                _logger.error(f"Row data: {sheet.row_values(row)}")

        # Log the number of failed rows
        _logger.info(f'Number of failed rows: {len(failed_rows)}')

        # Calculate and log checksum
        checksum = hashlib.md5(file_data).hexdigest()
        _logger.info(f'Checksum of the uploaded file: {checksum}')

    @api.model
    def create_single_invoice(self, invoice_vals):
        try:
            # The invoice_date is already in ISO format, no need to convert it again
            invoice = self.env['account.move'].sudo().create(invoice_vals)
            invoice.sudo().action_post()
            _logger.info(f'Successfully created invoice {invoice.id}')
        except Exception as e:
            _logger.error(f"Failed to create and post invoice: {e}")
            raise
