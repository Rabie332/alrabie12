from odoo import fields, models


class FolderShare(models.TransientModel):
    _name = "folder.share"
    _description = "Folder Share"

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
        """Share folder with other users."""
        context = self.env.context or {}
        for rec in self:
            model = rec.env[context.get("active_model")]
            folder = model.browse(context.get("active_id"))
            values = {}
            activity_name = "dms.mail_dms_folder_share"
            for user in self.shared_user_ids:
                values = {"shared_user_ids": [(4, user.id)]}
                folder.activity_schedule(activity_name, user_id=user.id)
            if values:
                folder.write(values)
