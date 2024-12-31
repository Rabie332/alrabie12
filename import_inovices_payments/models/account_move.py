from odoo import models, fields, api, _


class AccountMove(models.Model):
    _inherit = 'account.move'


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def action_invoice_import_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Import Old Invoices'),
            'res_model': 'invoice.import.wizard',
            'view_mode': 'form',
            'target': 'new',
        }

    def action_payment_import_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Import Old Payments'),
            'res_model': 'payment.import.wizard',
            'view_mode': 'form',
            'target': 'new',
        }

    def action_credit_note_import_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Import Old credit notes'),
            'res_model': 'credit.note.import.wizard',
            'view_mode': 'form',
            'target': 'new',
        }

    def action_expense_import_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Import Old Expenses'),
            'res_model': 'expense.import.wizard',
            'view_mode': 'form',
            'target': 'new',
        }

    def action_delete_journal_entries_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Delete Journal Entries'),
            'res_model': 'delete.journal.entries.wizard',
            'view_mode': 'form',
            'target': 'new',
        }

    def action_journal_entry_import_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Import Old Journal Entries'),
            'res_model': 'journal.entry.import.wizard',
            'view_mode': 'form',
            'target': 'new',
        }
