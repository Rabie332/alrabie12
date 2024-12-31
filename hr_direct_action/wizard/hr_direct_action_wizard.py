from odoo import fields, models


class HrDirectActionWizard(models.TransientModel):
    _name = "hr.direct.action.wizard"
    _description = "Hr Direct Action Wizard"

    partner_ids = fields.Many2many(
        "res.partner",
        string="Companies",
        required=True,
        domain=[("is_company", "=", True)],
    )

    def send_email(self):
        """Send email to partners selected"""
        template = self.env.ref(
            "hr_direct_action.mail_template_direct_action",
            raise_if_not_found=False,
        )
        if template and self._context.get("active_id"):
            for partner in self.partner_ids:
                template.email_to = partner.email
                template.send_mail(self._context.get("active_id"), force_send=True)
