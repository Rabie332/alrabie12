from odoo import api, models


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    @api.model
    def create(self, values):
        """Create Attachment from invoice."""
        attachment = super(IrAttachment, self).create(values)
        # make the attachment public to be downloaded by the client
        if attachment.res_model == "account.move":
            attachment.public = True
        return attachment
