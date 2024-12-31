from odoo import fields, models


class HrObligationSetting(models.Model):
    _inherit = "hr.obligation.setting"

    ####################################################################################
    # Fields
    ####################################################################################

    folder_ids = fields.Many2many("dms.folder", string="folders")


class DmsFolder(models.Model):
    _inherit = "dms.folder"

    def action_documents(self):
        """Get attachments for obligation."""
        obligation_setting = self.env["hr.obligation.setting"].search([], limit=1)
        attachment_action = self.env.ref("dms.folder_2_attachment_action")
        action = attachment_action.sudo().read()[0]
        if (
            obligation_setting
            and len(obligation_setting.folder_ids)
            and self.id in obligation_setting.folder_ids.ids
        ):
            action["context"] = {
                "default_folder_id": self.id,
                "default_res_model": "hr.obligation.setting",
                "default_res_id": obligation_setting.id,
            }
            action["domain"] = [
                ("res_model", "=", "hr.obligation.setting"),
                ("res_id", "=", obligation_setting.id),
                ("folder_id", "=", self.id),
            ]
        return action
