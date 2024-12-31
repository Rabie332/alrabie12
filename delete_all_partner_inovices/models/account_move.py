from odoo import models, fields, api, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_delete_invoices_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Delete Partner Invoices'),
            'res_model': 'invoice.deletion.wizard',
            'view_mode': 'form',
            'target': 'new',
        }
