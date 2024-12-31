from odoo import fields, models, api
# import logging

# _logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = "res.partner"

    employee_id_num_issue = fields.Integer(string="Employee ID Number Issue")
    employee_iqama_number = fields.Char(string="Employee Iqama Number")

    # @api.depends('name')
    # def _compute_employee_details(self):
    #     for record in self:
    #         if not record.name:
    #             _logger.info(f"Partner '{record.id}' has no name set, skipping employee details computation.")
    #             record.employee_id_num_issue = 0
    #             record.employee_iqama_number = False
    #             continue

    #         employee = self.env['hr.employee'].search([('display_name_en', '=', record.name)], limit=1)
    #         if employee:
    #             record.employee_id_num_issue = employee.ID_num_issue if employee.ID_num_issue else 0
    #             record.employee_iqama_number = employee.residence_id if employee.residence_id else False
    #         else:
    #             _logger.warning(f"No matching employee found for partner '{record.name}'.")
    #             record.employee_id_num_issue = 0
    #             record.employee_iqama_number = False
