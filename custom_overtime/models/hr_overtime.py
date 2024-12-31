import calendar
from datetime import date

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HrOvertime(models.Model):
    _inherit = "hr.overtime"
    
    
    def action_send_clone(self):
        """Send the request to be approved by the right users."""
        for request in self:
            if request.stage_id and request.state == "draft":
                request.stage_id = request._get_next_stage()
                request._onchange_stage_id()
                request.activity_update()

    def action_reset_to_draft(self):
        draft_stage_id = self.env['request.stage'].search([
            '|', ('name', '=', 'Send'), ('name', '=', 'موظف'),
            '|', ('name_dept', '=', 'overtime'), ('name_dept',
                                                            '=', 'overtime')
        ], limit=1).id
        if draft_stage_id:
            self.write({'state': 'draft', 'stage_id': draft_stage_id})
