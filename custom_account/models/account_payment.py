from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountPayment(models.Model):
    _inherit = "account.payment"
    
    
    destination_account_id = fields.Many2one(
      comodel_name='account.account',
      string='Destination Account',
      store=True, readonly=False,
      compute='_compute_destination_account_id',
      domain="[]",  # No restrictions
      check_company=True
      )

