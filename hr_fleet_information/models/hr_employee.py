from odoo import fields, models


class HrEmployeeBase(models.AbstractModel):
    _inherit = "hr.employee.base"

    driving_permit_number = fields.Char(string="Driving Permit Number", tracking=True)
    port_licence_number = fields.Char(string="Port Licence Number", tracking=True)
    port_licence_end_date = fields.Date(string="Port Licence Expiration Date", tracking=True)
    play_card_number = fields.Char(string="Play Card Number", tracking=True)
    play_card_end_date = fields.Date(string="Play Card Expiration Date", tracking=True)
