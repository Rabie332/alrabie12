from odoo import api, models


class IrAttachment(models.Model):
    _inherit = "ir.attachment"
    _description = "Attachments"

    @api.model_create_multi
    def create(self, vals_list):
        """Link the attachment with correct folder."""
        for vals in vals_list:
            res_model = vals.get("res_model", False)
            if res_model:
                model_id = (
                    self.env["ir.model"].sudo().search([("model", "=", res_model)])
                )
                folder_id = self.env["dms.folder"].search(
                    [("model_ids", "in", model_id.ids)], limit=1
                )
                if folder_id:
                    vals["folder_id"] = folder_id.id
        return super(IrAttachment, self).create(vals_list)
