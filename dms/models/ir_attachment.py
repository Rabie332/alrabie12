import mimetypes
import os

from odoo import _, api, fields, models
from odoo.tools import base64


class IrAttachment(models.Model):
    _name = "ir.attachment"
    _inherit = ["ir.attachment", "mail.thread", "mail.activity.mixin"]
    _description = "Attachments"

    doc_expiry_date = fields.Datetime(
        string='Attachment Expiration Date', required=True)
    code = fields.Char(string="Code", readonly=True)
    folder_id = fields.Many2one("dms.folder", string="Folder")
    type_id = fields.Many2one("ir.attachment.type", string="Document type")
    size = fields.Integer(string="Size", readonly=True)
    locked = fields.Boolean(string="Locked")
    secrecy_id = fields.Many2one("dms.secrecy", string="Secrecy")
    version_ids = fields.One2many(
        "ir.attachment.version", "document_id", string="Version"
    )
    shared_user_ids = fields.Many2many(
        "res.users",
        string="Employees",
    )
    extension = fields.Char(
        string="Extension", compute="_compute_extension", store=True
    )
    datas_viewer = fields.Binary(string="File preview", related="datas")

    @api.depends("mimetype")
    def _compute_extension(self):
        for record in self:
            if record.mimetype:
                record.extension = mimetypes.guess_extension(record.mimetype)

    @api.model
    def create(self, vals):
        """Add sequence and check if the folder_id is empty and fill it."""
        number_ir_attachment = self.env["ir.sequence"].next_by_code(
            "ir.attachment.seq")
        vals.update({"code": number_ir_attachment})

        if 'folder_id' not in vals and self._context.get('default_folder_id'):
            vals['folder_id'] = self._context['default_folder_id']
        return super(IrAttachment, self).create(vals)

    @api.onchange("datas")
    def _onchange_datas_fname(self):
        """Add name to ir.attachment from file name."""
        for attachment in self:
            if attachment.datas:
                attachment.size = len(base64.b64decode(attachment.datas))

    def action_send(self):
        """Send quotation by mail with using it's template."""
        compose_form = self.env.ref("mail.email_compose_message_wizard_form")
        template = self.env.ref("dms.attachment_mail_template")

        ctx = dict(
            default_model="ir.attachment",
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template.id,
            default_composition_mode="comment",
            default_attachment_ids=[(6, 0, [self.id])],
        )
        return {
            "name": _("Send Email"),
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "mail.compose.message",
            "views": [(compose_form.id, "form")],
            "view_id": compose_form.id,
            "target": "new",
            "context": ctx,
        }

    def _read_group_allowed_fields(self):
        result = super(IrAttachment, self)._read_group_allowed_fields()
        extra_allowed_fields = ["folder_id", "type_id"]
        result.extend(extra_allowed_fields)
        return result


class IrAttachmentType(models.Model):
    _name = "ir.attachment.type"
    _description = "Documents types"

    name = fields.Char(string="Name", required=1, translate=True)
    code = fields.Char(string="Code")


class IrAttachmentVersion(models.Model):
    _name = "ir.attachment.version"
    _description = "New version"
    _order = "version desc"

    version = fields.Integer(string="Version", required=1)
    datas = fields.Binary(string="File", required=True, attachment=True)
    document_id = fields.Many2one(
        "ir.attachment", string="Document", ondelete="cascade"
    )
    extension = fields.Char(related="document_id.extension")

    def download_attachment(self):
        """To download the file version from tree view."""
        for rec in self:
            # Remove extension to let odoo guess file extension: when versions have different extensions
            filename = os.path.splitext(rec.document_id.name)[0]
            return {
                "type": "ir.actions.act_url",
                "url": "/web/content?model=ir.attachment.version&field=datas&id=%s&filename=%s&download=true"
                % (rec.id, filename),
                "target": "new",
            }
