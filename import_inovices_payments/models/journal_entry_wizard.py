from odoo import models, api, fields
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


class JournalEntryWizard(models.TransientModel):
    _name = 'journal.entry.import.wizard'
    _description = 'Journal Entry Import Wizard'

    file = fields.Binary('File', required=True)
    wizard_desc = fields.Char(
        string="Excel Format", default="Excel format must be in this order: 'Entry Date', 'Account', 'Partner Name', 'Entry Ref', 'Debit Amount', 'Credit Amount', 'Entry Batch Number', 'Line With Taxes'", readonly=True)
    company = fields.Many2one(
        'res.company', required=True, string='Entry Company')
    journal = fields.Many2one(
        'account.journal', required=True, string='Entry Journal')
    taxes = fields.Many2many('account.tax', string='Entry Taxes')
    tax_type = fields.Selection(
        [("debit", "Debit"), ("credit", "Credit")],
        string="Tax Type"
    )

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
            account_code = str(sheet.cell_value(row, 1)).split('.')[0].strip()
            partner_name = sheet.cell_value(row, 2).strip()
            ref = sheet.cell_value(row, 3)
            debit_amount = float(sheet.cell_value(row, 4))
            credit_amount = float(sheet.cell_value(row, 5))
            batch_number = str(sheet.cell_value(row, 6)).strip()
            line_with_taxes = str(sheet.cell_value(
                row, 7)) == 'TRUE'

            if batch_number not in entries:
                entries[batch_number] = {
                    'date': entry_date,
                    'ref': ref,
                    'journal_id': self.journal.id,
                    'move_type': 'entry',
                    'line_ids': [],
                    'company_id': self.company.id,
                }

            account_id = self.env['account.account'].search(
                [('code', '=', account_code), ('company_id', '=', self.company.id)], limit=1)
            if not account_id:
                raise UserError(
                    _('Account with code %s not found.') % account_code)

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

            journal_entry_line_vals = {
                'account_id': account_id.id,
                'name': ref,
                'debit': debit_amount,
                'credit': credit_amount,
                'partner_id': partner.id if partner else False,
                'tax_ids': [(6, 0, self.taxes.ids)] if line_with_taxes else [],
            }

            entries[batch_number]['line_ids'].append(
                (0, 0, journal_entry_line_vals))

        for batch_number, journal_entry_vals in entries.items():
            self.create_single_journal_entry(journal_entry_vals)

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
            raise UserError(
                _("Failed to create and post journal entry: %s") % e)
