from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime
import logging
import time
_logger = logging.getLogger(__name__)


class DeleteJournalEntriesWizard(models.TransientModel):
    _name = 'delete.journal.entries.wizard'
    _description = 'Delete Journal Entries Wizard'

    employee_id = fields.Many2one(
        'hr.employee', string='Employee', required=True)
    datetime_from = fields.Datetime(string='Datetime From', required=True)
    datetime_to = fields.Datetime(string='Datetime To', required=True)

    def start_background_job(self):
        # Enqueue the job for background processing
        self.with_delay().delete_journal_entries()

    def delete_journal_entries(self):
        company_name = "Al-Diyafah Plus Co"
        company = self.env['res.company'].search(
            [('name', '=', company_name)], limit=1)
        if not company:
            raise UserError(_('Company %s not found.') % company_name)

        if self.datetime_from > self.datetime_to:
            raise UserError(
                _("The start datetime must be before the end datetime."))

        employee = self.employee_id
        user = employee.user_id
        if not user:
            raise UserError(
                _("The selected employee does not have an associated user."))

        journal_entries = self.env['account.move'].search([
            ('create_uid', '=', user.id),
            ('create_date', '>=', self.datetime_from),
            ('create_date', '<=', self.datetime_to),
            ('company_id', '=', company.id),
            ('state', '=', 'draft')
        ])
        if not journal_entries:
            raise UserError(
                _("No journal entries found for the selected criteria."))

        for journal_entry in journal_entries:
            try:
                journal_entry.button_cancel()
                journal_entry.unlink()
            except Exception as e:
                _logger.error('Failed to delete entry %s: %s',
                              journal_entry.id, str(e))
