from odoo import models, fields, api, _
import logging
from datetime import timedelta  
from odoo.exceptions import UserError, ValidationError
_logger = logging.getLogger(__name__)


class CustomPurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    def find_and_send_request(self):
        pm_stage_id = self.env['request.stage'].search([
            '|', ('name', '=', 'Purchase Department'), ('name', '=', 'قسم المشتريات')], limit=1).id
        for request in self:
            if request.stage_id:
                request.stage_id = pm_stage_id
                request._onchange_stage_id()
                if request.state != "done":
                    request.activity_update()
                else:
                    request.action_feedback()
        return True
