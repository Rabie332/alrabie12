from odoo import fields, models


class IrAttachmentVersionUpload(models.TransientModel):
    _name = "ir.attachment.version.upload"
    _description = "Attachment Wizard"

    name = fields.Char(string="Name", required=True)
    datas = fields.Binary(string="File", required=True)
    store_fname = fields.Char("Stored Filename")

    def upload_version(self):
        """Add new version to document."""
        context = self.env.context or {}
        attachment_version_obj = self.env["ir.attachment.version"]
        for wiz in self:
            if (
                wiz.datas
                and context.get("active_id", False)
                and context.get("active_model", False)
            ):
                model = self.env[context.get("active_model")]
                rec = model.browse(context.get("active_id"))
                if rec.version_ids:
                    version = rec.version_ids[0].version + 1
                else:
                    version = 1
                values = {"version": version, "document_id": rec.id, "datas": rec.datas}
                attachment_version_obj.create(values)
                rec.write({"datas": wiz.datas, "name": wiz.name})


class IrattachmentVersionList(models.TransientModel):
    _name = "ir.attachment.version.list"
    _description = "Display version of documents"

    def get_default_version_ids(self):
        """Get default version_ids."""
        context = self.env.context or {}
        model = self.env[context.get("active_model")]
        rec = model.browse(context.get("active_id"))
        return rec.version_ids

    version_ids = fields.Many2many(
        "ir.attachment.version", string="Version", default=get_default_version_ids
    )
