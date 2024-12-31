from odoo import fields, models


class MailActivityType(models.Model):
    _inherit = "mail.activity.type"

    category = fields.Selection(
        selection_add=[("validation", "Validation"), ("feedback", "Feedback")]
    )


class MailActivity(models.Model):
    _inherit = "mail.activity"

    active = fields.Boolean(default=True, string="Active")
