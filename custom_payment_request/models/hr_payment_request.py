from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class CustomHrPaymentRequest(models.Model):
    _inherit = 'hr.payment.request'

    is_paid = fields.Boolean("Is Paid", copy=False, default=False)
    due_date = fields.Date(string="Due Date",
                           required=True,
                           states={"draft": [("readonly", False)]},)

    def action_to_ceo(self):
        ceo_stage_record = self.env['request.stage'].search([
            '|', ('name', '=', 'Finance Department'), ('name',
                                                       '=', 'الادارة المالية'),
            '|', ('name_dept', '=', 'Payment Department'), ('name_dept',
                                                            '=', 'Payment Department')
        ], limit=1)
        ceo_stage_id = ceo_stage_record.id

        for request in self:
            if request.stage_id:
                request.stage_id = ceo_stage_id
                request._onchange_stage_id()

                # If the request is not in a 'done' state, update activities
                if request.state != "done":
                    request.activity_update()
                else:
                    request.action_feedback()
        return True

    def action_reset_to_draft(self):
        draft_stage_id = self.env['request.stage'].search([
            '|', ('name', '=', 'Draft'), ('name', '=', 'مسودة'),
            '|', ('name_dept', '=', 'Payment Department'), ('name_dept',
                                                            '=', 'Payment Department')
        ], limit=1).id
        if draft_stage_id:
            self.write({'state': 'draft', 'stage_id': draft_stage_id})
