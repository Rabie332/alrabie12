from odoo import fields, models


class ResourceCalendarInherit(models.Model):
    _inherit = "resource.calendar"

    late = fields.Float(string="Delay Hours Allowed")
    early_exit = fields.Float(string="Early Exit Allowed")
