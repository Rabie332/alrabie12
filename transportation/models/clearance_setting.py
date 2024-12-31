from odoo import fields, models


class ClearanceLockSetting(models.Model):
    _name = "clearance.lock.setting"
    _description = "Clearance Lock Settings"

    name = fields.Char(string="Name", required=1)
    requirement_ids = fields.Many2many(
        "clearance.lock.requirement", string="Requirements", required=1
    )
    company_id = fields.Many2one(
        "res.company", "Company", default=lambda self: self.env.company, required=1
    )
    active = fields.Boolean(default=True, string="Active")


class ClearanceLockRequirement(models.Model):
    _name = "clearance.lock.requirement"
    _description = "Clearance Lock Requirements"

    name = fields.Char(string="Name ", required=1)
    need_attachment = fields.Boolean(string="Need Attachment")
    active = fields.Boolean(default=True, string="Active")
