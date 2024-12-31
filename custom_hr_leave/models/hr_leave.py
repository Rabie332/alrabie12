from odoo import api, fields, models



class HrDeputation(models.Model):
    _inherit = 'hr.leave'

    def action_reset_to_draft(self):
            draft_stage_id = self.env['request.stage'].search([
                '|', ('name', '=', 'Draft'), ('name', '=', 'مسودة'),
                '|', ('name_dept', '=', 'Leave Stages'), ('name_dept', '=', 'Leave Stages')
                ], limit=1).id
            if draft_stage_id:
                self.write({'state': 'draft', 'stage_id': draft_stage_id})