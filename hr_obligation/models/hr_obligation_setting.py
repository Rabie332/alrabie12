from lxml import etree

from odoo import _, api, fields, models


class HrObligationSetting(models.Model):
    _name = "hr.obligation.setting"
    _description = "Obligation Setting"

    ####################################################################################
    # Fields
    ####################################################################################
    name = fields.Char(
        string="Name", default="Policies and Regulations", translate=True
    )
    attachment_ids = fields.Many2many("ir.attachment", string="Attachments")

    ####################################################################################
    # Methodes
    ####################################################################################
    
    @api.model
    def create(self, vals):
        # Creating the record
        record = super(HrObligationSetting, self).create(vals)
        # Fix attachment ownership for newly created record
        if 'attachment_ids' in vals:
            attachments = self.env['ir.attachment'].browse(vals['attachment_ids'][0][2])
            attachments.write({'res_model': self._name, 'res_id': record.id})
        return record

    def write(self, vals):
        # Updating the record
        result = super(HrObligationSetting, self).write(vals)
        # Fix attachment ownership for existing records
        if 'attachment_ids' in vals:
            attachments = self.env['ir.attachment'].browse(vals['attachment_ids'][0][2])
            attachments.write({'res_model': self._name, 'res_id': self.id})
        return result
    
    def button_setting(self):
        """Show view form for obligation main settings.

        :return: Dictionary contain view form of hr.obligation.setting
        """
        obligation_setting = self.env["hr.obligation.setting"].search([], limit=1)
        if obligation_setting:
            value = {
                "name": _("Obligation Setting"),
                "view_type": "form",
                "view_mode": "form",
                "res_model": "hr.obligation.setting",
                "view_id": False,
                "type": "ir.actions.act_window",
                "res_id": obligation_setting.id,
            }
            return value

    def button_open_policies_regulations(self):
        """Show view form for obligation main settings.

        :return: Dictionary contain view form of hr.obligation.setting
        """
        obligation_setting = self.env["hr.obligation.setting"].search([], limit=1)
        if obligation_setting:
            value = {
                "name": _("Obligation Setting"),
                "view_type": "form",
                "view_mode": "form",
                "res_model": "hr.obligation.setting",
                "view_id": False,
                "type": "ir.actions.act_window",
                "context": {"no_display_create_edit": True},
                "res_id": obligation_setting.id,
            }
            return value

    ####################################################################################
    # ORM Methodes
    ####################################################################################

    @api.model
    def fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        """fields_view_get to remove create and edit and delete
        from menu HrObligationSetting in self service."""
        res = super(HrObligationSetting, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu
        )
        if self.env.context.get("no_display_create_edit"):
            doc = etree.XML(res["arch"])
            for node in doc.xpath("//tree"):
                node.set("create", "0")
                node.set("edit", "0")
                node.set("duplicate", "0")
            for node in doc.xpath("//form"):
                node.set("create", "0")
                node.set("edit", "0")
                node.set("duplicate", "0")
            res["arch"] = etree.tostring(doc, encoding="unicode")
        return res
