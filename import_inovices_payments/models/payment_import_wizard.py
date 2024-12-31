import base64
import xlrd
import json
import logging
import hashlib
from io import BytesIO
import pandas as pd
from odoo.exceptions import UserError
from odoo import models, fields, api, _
from datetime import datetime
import time


_logger = logging.getLogger(__name__)


class PaymentImportWizard(models.TransientModel):
    _name = 'payment.import.wizard'
    _description = 'Payment Import Wizard'

    wizard_desc = fields.Char(
        string="Excel Format", default="Excel format must be in this order: 'Payment Date', 'Account Name', 'Label', 'Customer', 'Amount'", readonly=True)
    file = fields.Binary('File', required=True)

    company = fields.Many2one(
        'res.company', required=True, string='Payment Company')

    journal = fields.Many2one(
        'account.journal', required=True, string='Payment Journal')

    def import_file(self):
        if not self.file:
            raise UserError(_("Please upload a file to import."))

        file_data = base64.b64decode(self.file)
        encoded_file_data = base64.b64encode(file_data).decode('utf-8')
        self.with_delay().process_file(encoded_file_data)

    @api.model
    def process_file(self, encoded_file_data):
        _logger.info('Start processing payment file')
        file_data = base64.b64decode(encoded_file_data.encode('utf-8'))
        workbook = xlrd.open_workbook(file_contents=file_data)
        sheet = workbook.sheet_by_index(0)

        currency_name = "SAR"
        currency = self.env['res.currency'].search(
            [('name', '=', currency_name)], limit=1)
        if not currency:
            raise UserError(_('Currency %s not found.') % currency_name)
        failed_rows = []

        for row in range(1, sheet.nrows):
            try:
                payment_date = xlrd.xldate.xldate_as_datetime(
                    sheet.cell_value(row, 0), workbook.datemode)
                account_code = str(
                    sheet.cell_value(row, 1)).split('.')[0].strip()
                ref = sheet.cell_value(row, 2)
                partner_name = sheet.cell_value(row, 3).strip()
                amount_before_taxes = float(sheet.cell_value(row, 4))

                partner = None
                if partner_name:
                    partner = self.env['res.partner'].search(
                        [('name', '=', partner_name), ('company_id', '=', self.company.id)], limit=1)
                    if not partner:
                        partner = self.env['res.partner'].create(
                            {'name': partner_name, 'company_id': self.company.id})
                    elif partner.company_id != self.company:
                        raise UserError(
                            _('Partner %s belongs to a different company.') % partner_name)

                account_id = self.env['account.account'].search(
                    [('code', '=', account_code), ('company_id', '=', self.company.id)], limit=1)
                if not account_id:
                    raise UserError(
                        _('account with code %s not found.') % account_code)

                payment_vals = {
                    'payment_type': 'inbound',
                    'partner_id': partner.id,
                    'partner_type': 'customer',
                    'destination_account_id': account_id.id,
                    'amount': amount_before_taxes,
                    'date': payment_date,
                    'journal_id': self.journal.id,
                    'ref': ref,
                    'currency_id': currency.id,
                }

                self.create_single_payment(payment_vals)
            except Exception as e:
                failed_rows.append((row, str(e)))
                _logger.error(f"Failed to process row {row}: {e}")

        _logger.info(f'Number of failed rows: {len(failed_rows)}')

        checksum = hashlib.md5(file_data).hexdigest()
        _logger.info(f'Checksum of the uploaded file: {checksum}')

    @api.model
    def create_single_payment(self, payment_vals):
        try:
            payment_vals['date'] = payment_vals['date'].isoformat()
            payment = self.env['account.payment'].create(payment_vals)
            payment.action_post()
            _logger.info('Finished processing a payment')
        except Exception as e:
            _logger.error(f"Failed to create and post payment: {e}")
            raise
