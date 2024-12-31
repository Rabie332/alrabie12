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


class ExpenseImportWizard(models.TransientModel):
    _name = 'expense.import.wizard'
    _description = 'Expense Import Wizard'

    file = fields.Binary('File', required=True)
    wizard_desc = fields.Char(
        string="Excel Format", default="Excel format must be in this order: 'Entry Date', 'Entry Ref', 'Debit Account', 'Credit Account', 'Partner Name', 'Amount before taxes', 'Entry Batch Number'", readonly=True)
    company = fields.Many2one(
        'res.company', required=True, string='Entry Company')
    journal = fields.Many2one(
        'account.journal', required=True, string='Entry Journal')
    taxes = fields.Many2many(
        'account.tax', string='Entry Taxes')
    tax_type = fields.Selection(
        [("debit", "Debit"), ("credit", "Credit")], string="Tax Type", required=True)

    def import_file(self):
        if not self.file:
            raise UserError(_("Please upload a file to import."))

        file_data = base64.b64decode(self.file)
        self.process_file(file_data)

    @api.model
    def process_file(self, file_data):
        _logger.info('Start processing expense file')
        workbook = xlrd.open_workbook(file_contents=file_data)
        sheet = workbook.sheet_by_index(0)

        entries = {}
        for row in range(1, sheet.nrows):
            entry_date = xlrd.xldate.xldate_as_datetime(
                sheet.cell_value(row, 0), workbook.datemode)
            ref = sheet.cell_value(row, 1)
            debit_account_code = str(
                sheet.cell_value(row, 2)).split('.')[0].strip()
            credit_account_code = str(
                sheet.cell_value(row, 3)).split('.')[0].strip()
            partner_name = sheet.cell_value(row, 4).strip()
            amount_before_taxes = float(sheet.cell_value(row, 5))
            batch_number = str(sheet.cell_value(row, 6)).strip()

            if batch_number not in entries:
                entries[batch_number] = {
                    'date': entry_date,
                    'ref': ref,
                    'journal_id': self.journal.id,
                    'move_type': 'entry',
                    'line_ids': [],
                    'company_id': self.company.id,
                }

            debit_account = self.env['account.account'].search(
                [('code', '=', debit_account_code), ('company_id', '=', self.company.id)], limit=1)
            if not debit_account:
                raise UserError(
                    _('Debit account with code %s not found.') % debit_account_code)

            credit_account = self.env['account.account'].search(
                [('code', '=', credit_account_code), ('company_id', '=', self.company.id)], limit=1)
            if not credit_account:
                raise UserError(
                    _('Credit account with code %s not found.') % credit_account_code)

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

            tax_amount = sum(tax.amount / 100.0 *
                             amount_before_taxes for tax in self.taxes)
            total_amount = amount_before_taxes + tax_amount

            if self.tax_type == "debit":
                debit_line_vals = {
                    'account_id': debit_account.id,
                    'name': ref,
                    'debit': total_amount,
                    'credit': 0.0,
                    # 'tax_ids': [(6, 0, self.taxes.ids)],
                }
                credit_line_vals = {
                    'account_id': credit_account.id,
                    'name': ref,
                    'debit': 0.0,
                    'credit': amount_before_taxes,
                }
            elif self.tax_type == "credit":
                debit_line_vals = {
                    'account_id': debit_account.id,
                    'name': ref,
                    'debit': amount_before_taxes,
                    'credit': 0.0,
                }
                credit_line_vals = {
                    'account_id': credit_account.id,
                    'name': ref,
                    'debit': 0.0,
                    'credit': total_amount,
                    # 'tax_ids': [(6, 0, self.taxes.ids)],
                }

            if partner:
                debit_line_vals['partner_id'] = partner.id
                credit_line_vals['partner_id'] = partner.id

            entries[batch_number]['line_ids'].append((0, 0, debit_line_vals))
            entries[batch_number]['line_ids'].append((0, 0, credit_line_vals))

        for batch_number, journal_entry_vals in entries.items():
            self.create_single_journal_entry(journal_entry_vals)

        _logger.info(f'Number of failed rows: {len(entries)}')
        checksum = hashlib.md5(file_data).hexdigest()
        _logger.info(f'Checksum of the uploaded file: {checksum}')

    @api.model
    def create_single_journal_entry(self, journal_entry_vals):
        try:
            journal_entry_vals['date'] = journal_entry_vals['date'].isoformat()
            journal_entry = self.env['account.move'].create(journal_entry_vals)
            journal_entry.action_post()
            _logger.info(
                f'Successfully created journal entry {journal_entry.id}')
        except Exception as e:
            _logger.error(f"Failed to create and post journal entry: {e}")
            raise
