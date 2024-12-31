from odoo import fields, models


class InstallmentTemplate(models.Model):
    _name = "installment.template"
    _description = "Installment Template"
    _inherit = ["mail.thread"]

    name = fields.Char(string="Name", size=64, required=True)
    duration_month = fields.Integer(string="Month")
    duration_year = fields.Integer(string="Year")
    annual_raise = fields.Integer(string="Annual Raise %")
    repetition_rate = fields.Integer(string="Repetition Rate (month)", default=1)
    adv_payment_rate = fields.Integer(string="Advance Payment %")
    deduct = fields.Boolean(string="Deducted from amount?")
