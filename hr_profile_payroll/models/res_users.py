from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    payslip_count = fields.Integer(
        compute="_compute_payslip_count",
        string="Payslip Count",
        groups="base.group_user",
    )

    def _compute_payslip_count(self):
        for user in self:
            slips = user.employee_id.slip_ids
            user.payslip_count = len(slips.filtered(lambda l: l.state == "done"))
