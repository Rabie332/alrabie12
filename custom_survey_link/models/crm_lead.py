from odoo import api, exceptions, fields, models, _


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    def action_open_survey_responses(self):
        self.ensure_one()
        surveys = self.env['survey.user_input'].search([
            ('partner_id', '=', self.partner_id.id),
            ('email', '=', self.email_from)
        ])
        action = {
            'name': _('Survey Responses'),
            'type': 'ir.actions.act_window',
            'res_model': 'survey.user_input',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', surveys.ids)],
            'target': 'current',
        }
        return action
