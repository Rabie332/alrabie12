from odoo import _, models, fields, api
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError

class ClearanceRequest(models.Model):
    _inherit = 'clearance.request'


    extra_charges_customs_statement = fields.Selection(
        [
            ("extra_charge", "Yes"),
            ("not_extra_charge", "No"),
        ],
        string="Are There Any Extra Charges while in Customs Statement?", 
        tracking=True,
    )
    
    extra_charges_customs_statement_wizard_status = fields.Boolean(
        string="Invoice Created for Extra Customs Statement Charges",
        default=False,
    )
    
    request_priority = fields.Selection(
        [
            ("not_urgent", "Not Urgent"),
            ("urgent", "Urgent"),
        ],
        string="Transport Priority",
        tracking=True,
    )
    
    clearance_request_priority = fields.Selection(
        [
            ("not_urgent", "Not Urgent"),
            ("urgent", "Urgent"),
        ],
        string="Clearance Priority",
        tracking=True,
    )
    
    extra_charges_delivery = fields.Selection(
        [
            ("extra_charge", "Yes"),
            ("not_extra_charge", "No"),
        ],
        string="Are There Any Extra Charges while in Delivery?", 
        tracking=True,
    )
    
    extra_charges_delivery_wizard_status = fields.Boolean(
        string="Invoice Created for Extra Delivery Charges",
        default=False,
    )


    def action_transport(self):
      for request in self:
            if request.extra_charges_customs_statement == "extra_charge" and request.extra_charges_customs_statement_wizard_status == False:
                raise ValidationError(_("You must handle extra charges and create an invoice before completing Custom Statement."))
            
      return super(ClearanceRequest, self).action_transport()
      
    def action_delivery_done(self):
        for request in self:
            if request.extra_charges_delivery == "extra_charge" and request.extra_charges_delivery_wizard_status == False:
                raise ValidationError(_("You must handle extra charges and create an invoice before completing delivery."))

        return super(ClearanceRequest, self).action_delivery_done()
      

    def action_open_extra_charges_wizard(self):
        # This method should return an action that opens the wizard
        return {
            'type': 'ir.actions.act_window',
            'name': 'Extra Charges',
            'view_mode': 'form',
            'res_model': 'clearance.extra.charges.wizard',
            'target': 'new',
            'context': {
                'default_clearance_request_id': self.id,
            },
        }