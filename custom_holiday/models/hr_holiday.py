from odoo import models, fields, api
from datetime import date

class HrHoliday(models.Model):
    _name = 'hr.holiday'
    _rec_name = 'employee_id'
    
    
    employee_id = fields.Many2one('hr.employee',string="Employee", help="Link to the employee")
    residence_num = fields.Char(string="Residence Number", related="employee_id.residence_id")
    identification_num = fields.Char(string="Identification Number", related="employee_id.identification_id")
    company_id = fields.Many2one("res.company", string="Company", related="employee_id.company_id")
    # employee_vacation_type = fields.Selection(related="employee_id.employee_vacation_type",string="Employee Vacation Type")
    job_position = fields.Char(string='Job Position', related="employee_id.job_title")
    first_contract_date = fields.Date(string="Contract Day", related="employee_id.first_contract_date")
    years_of_service = fields.Float(string="Years Of Service", compute='_compute_years_of_service')
    total_vacation_days = fields.Float(string="Total Vacation Days", compute='_compute_total_vacation_days')
    used_days = fields.Integer(string="Used Days", compute='_compute_used_days')
    final_balance = fields.Float(string="Final Balance", compute="_compute_final_balance")
    note = fields.Char(string="Note")
    
    @api.depends('first_contract_date')
    def _compute_years_of_service(self):
        for record in self:
            if record.first_contract_date:
                delta = date.today() - fields.Date.from_string(record.first_contract_date)
                record.years_of_service = delta.days / 365.25  # Using 365.25 to account for leap years
            else:
                record.years_of_service = 0.0
    
    @api.depends('years_of_service')
    def _compute_total_vacation_days(self):
        for record in self:
            is_saudi = record.employee_id.is_saudian
            if record.years_of_service and is_saudi == True:
                record.total_vacation_days = record.years_of_service * 30
            elif record.years_of_service > 5 and is_saudi == False:
                record.total_vacation_days = record.years_of_service * 30
            elif record.years_of_service < 5 and is_saudi == False:
                record.total_vacation_days = record.years_of_service * 21
            else:
                record.total_vacation_days = 0.0
                
    @api.depends('employee_id')
    def _compute_used_days(self):
        Leave = self.env['hr.leave']
        for record in self:
            leaves = Leave.search([
                ('employee_id', '=', record.employee_id.id),
                ('holiday_status_id.code', '=', '0001'),
                ('state', '=', 'done'), 
            ])
            record.used_days = sum(leaves.mapped('number_of_days'))
    
    @api.depends('total_vacation_days', 'used_days')
    def _compute_final_balance(self):
        for record in self:
            record.final_balance = record.total_vacation_days - record.used_days
        
    
                
    

