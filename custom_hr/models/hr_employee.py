from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class HrEmployeeCustom(models.Model):
    _inherit = 'hr.employee'

    job_title = fields.Char(required=True, translate=True, tracking=True)
    national_address = fields.Char(string="National Address", tracking=True)
    emp_job_title_en = fields.Char(
        string="Job Position (English)", tracking=True)
    ID_num_issue = fields.Integer(string="Num Of Time Issued", tracking=True)

    def start_background_job_expired_stay(self):
        self.set_expired_stay_job_que()

    @api.model
    def set_expired_stay_job_que(self):
        today = fields.Date.context_today(self)
        employees = self.env["hr.employee"].sudo().search([])
        for employee in employees:
            # Handle the address_home_id singleton issue
            if len(employee.address_home_id) > 1:
                _logger.warning(
                    f"Multiple address_home_id records found for employee {employee.id}")
                employee.address_home_id = employee.address_home_id[0]
            if employee.residence_end_date:
                try:
                    if employee.residence_end_date <= today:
                        employee.expired_stay = True
                    elif (employee.residence_end_date - today).days <= 10:
                        employee.expired_stay = True
                    else:
                        employee.expired_stay = False
                except Exception as e:
                    _logger.error(
                        f"Error processing employee {employee.id}: {e}")
                    raise
