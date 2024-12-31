from odoo.exceptions import UserError
from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class InvoiceDeletionWizard(models.TransientModel):
    _name = 'invoice.deletion.wizard'
    _description = 'Invoice Deletion Wizard'

    partner_id = fields.Many2one(
        'res.partner', string='Partner', required=True)

    def start_background_job(self):
        # Enqueue the job for background processing
        partner_id = self.partner_id.id
        self.with_delay().delete_invoices(partner_id)

    @api.model
    def delete_invoices(self, partner_id):
        partner = self.env['res.partner'].browse(partner_id)
        invoices = self.search_partner_invoices(partner)
        for invoice in invoices:
            try:
                if invoice.state == 'posted':
                    invoice.button_draft()
                    invoice.button_cancel()
                invoice.unlink()
                _logger.info('Deleted invoice %s for partner %s',
                             invoice.id, partner.name)
            except Exception as e:
                _logger.error('Failed to delete invoice %s: %s',
                              invoice.id, str(e))

        _logger.info('Finished deleting invoices for partner %s', partner.name)

    def search_partner_invoices(self, partner):
        invoices = self.env['account.move'].search(
            [('partner_id', '=', partner.id), ('move_type', '=', 'out_invoice')])

        if not invoices:
            raise UserError(_("No invoices found for the selected partner."))

        return invoices
