import logging
from odoo import models, api, fields

_logger = logging.getLogger(__name__)


class SurveyUserInput(models.Model):
    _inherit = 'survey.user_input'

    @api.model
    def create(self, vals):
        record = super(SurveyUserInput, self).create(vals)
        _logger.info('Survey User Input Created: %s', record.id)
        return record

    def write(self, vals):
        res = super(SurveyUserInput, self).write(vals)
        for record in self:
            if 'state' in vals and vals['state'] == 'done':
                _logger.info('Survey User Input Completed: %s', record.id)
                record.link_to_partner()
        return res

    def link_to_partner(self):
        for record in self:
            _logger.info('Linking to Partner for Survey ID: %s',
                         record.survey_id.id)
            _logger.info('User Input Lines: %s', record.user_input_line_ids)
            for line in record.user_input_line_ids:
                _logger.info('Line Data: %s', line.read())

            name_answer = self.get_answer(record, 'Name')
            email_answer = self.get_answer(record, 'Email')

            _logger.info('Name Answer: %s', name_answer)
            _logger.info('Email Answer: %s', email_answer)

            if name_answer and email_answer:
                name = name_answer
                email = email_answer

                partner = self.env['res.partner'].sudo().search(
                    [('name', '=', name), ('email', '=', email)], limit=1)
                if partner:
                    record.partner_id = partner.id
                    record.email = partner.email
                else:
                    partner = self.env['res.partner'].sudo().create({
                        'name': name,
                        'email': email,
                    })
                    record.partner_id = partner.id
                    record.email = partner.email

                self.create_crm_lead(partner, email)

    def get_answer(self, record, question_title):
        answer_line = record.user_input_line_ids.filtered(
            lambda l: l.question_id.title == question_title and l.survey_id.id == record.survey_id.id
        )
        if answer_line:
            _logger.info('Answer Line for %s: %s', question_title, answer_line.read([
                'value_char_box'
            ]))
            if answer_line[0].value_char_box:
                return answer_line[0].value_char_box
            elif answer_line[0].value_char_box:
                return answer_line[0].value_char_box
        return False

    def create_crm_lead(self, partner, email):
        lead_vals = {
            'name': f'Lead for {partner.name}',
            'partner_id': partner.id,
            'email_from': email,
            'description': 'Lead created from survey response',
            'company_id': self.survey_id.company_id.id,
            'user_id': False
        }
        self.env['crm.lead'].sudo().create(lead_vals)
        _logger.info(
            'CRM Lead Created for Partner ID: %s, Email: %s', partner.id, email)
