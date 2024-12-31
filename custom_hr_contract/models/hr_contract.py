from odoo import models, fields

class Contract(models.Model):
    _inherit = 'hr.contract'
    
    wage = fields.Monetary('Gross Wage', required=True, tracking=True, help="Employee's monthly gross wage.")
    social_insurance = fields.Monetary(string='Social Insurance', readonly=True, compute='_compute_net_wage')
    housing_allowance = fields.Float(string='Housing Allowance', readonly=True, compute='_compute_net_wage')
    wage_net = fields.Float("Net Wage", digits="Payroll", readonly=True, compute='_compute_net_wage')
    
    def _compute_net_wage(self):
        for contract in self:
            total_bonus = getattr(contract, 'total_bonus', 0.0)
            wage_with_bonus = contract.wage + total_bonus

            # Default calculation for housing allowance unless overridden below
            housing_allowance_found = False

            for allowance in contract.allowances_ids:
                if allowance.rule_id.code == "ALWH":
                    contract.housing_allowance = allowance.amount
                    housing_allowance_found = True
                    break

            if not housing_allowance_found:
                # Calculate default housing allowance if specific allowance not found
                contract.housing_allowance = contract.wage * 0.25

            if contract.struct_id.code == 'BASE_SAUDI':
                social_insurance_rate = 0.0975
                social_insurance_cap = 4500
                wage_before_gosi = contract.wage + contract.housing_allowance
                social_insurance = min(wage_before_gosi * social_insurance_rate, social_insurance_cap)
                
                contract.social_insurance = social_insurance
                contract.wage_net = wage_with_bonus - social_insurance
            else:
                # Default values if struct_id code is not 'BASE_SAUDI'
                contract.social_insurance = 0
                contract.wage_net = wage_with_bonus

                
                