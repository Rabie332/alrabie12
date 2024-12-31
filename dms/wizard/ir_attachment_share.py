from odoo import _, fields, models
from odoo.exceptions import ValidationError


class IrAttachmentShare(models.TransientModel):
    _name = "ir.attachment.share"
    _description = "Attachment Share"

    shared_user_ids = fields.Many2many(
        "res.users",
        string="Employees",
        domain=lambda self: [
            "|",
            ("company_id", "=", False),
            ("company_id", "=", self.env.company.id),
        ],
    )

    def action_share(self):
        """Share document with other users."""
        context = self.env.context or {}
        for rec in self:
            model = self.env[context.get("active_model")]
            document_id = model.browse(context.get("active_id"))
            activity_name = "dms.mail_ir_attachment_share"
            values = {}
            for user_id in rec.shared_user_ids:
                if document_id.secrecy_id.group_ids and not any(
                    group_id.id in user_id.groups_id.ids
                    for group_id in document_id.secrecy_id.group_ids
                ):
                    raise ValidationError(
                        _(
                            "The employee %s cannot read this document because it contains "
                            + "a secret degree that is not available to him."
                        )
                        % user_id.name
                    )
                else:
                    values = {"shared_user_ids": [(4, user_id.id)]}
            if values:
                document_id.write(values)
                for user in self.shared_user_ids:
                    document_id.activity_schedule(activity_name, user_id=user.id)
