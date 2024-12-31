from odoo import api, fields, models

class APIMessageWizard(models.TransientModel):
    _name = 'api.message.wizard'
    _description = 'API Response Message'

    message = fields.Text(string='Message')

    def action_ok(self):
        """Close the wizard"""
        return {'type': 'ir.actions.act_window_close'}
