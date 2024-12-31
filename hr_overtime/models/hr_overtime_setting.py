from odoo import _, fields, models


class HrOvertimeSetting(models.Model):
    _name = "hr.overtime.setting"
    _description = "Overtime Mandate setting"

    name = fields.Char(string="Name", translate=True)
    hour_number_mandate = fields.Integer(string="Hours number mandate")
    min_hour_mandate = fields.Integer(string="Minimum Hours Per Request")
    max_hour_month = fields.Integer(string="Maximum Hours Per Month")
    type = fields.Selection(
        [
            ("overtime", "Overtime"),
            ("mandate", "Mandate"),
        ],
        string="Type",
    )
    min_hour_day = fields.Integer(string="Minimum Hours Per Day")
    max_hour_day = fields.Integer(string="Maximum Hours Per Day")
    min_hour_weekend = fields.Integer(string="Minimum Hours Per weekend")
    max_hour_weekend = fields.Integer(string="Maximum Hours Per weekend")
    max_hour_month = fields.Integer(string="Maximum Hours Per Month")

    def action_overtime_mandate_setting(self):
        """Show view form for overtime main settings.

        :return: Dictionary contain view form of hr.overtime.setting with type mandate
        """
        overtime_mandate_setting = self.env["hr.overtime.setting"].search(
            [("type", "=", "mandate")], limit=1
        )
        if overtime_mandate_setting:
            value = {
                "name": _("Overtime mandate setting"),
                "view_type": "form",
                "view_mode": "form",
                "res_model": "hr.overtime.setting",
                "view_id": False,
                "type": "ir.actions.act_window",
                "res_id": overtime_mandate_setting.id,
            }
            return value

    def action_overtime_setting(self):
        """Show view form for overtime main setting.

        :return: Dictionary contain view form of hr.overtime.setting with type overtime
        """
        overtime_setting = self.env["hr.overtime.setting"].search(
            [("type", "=", "overtime")], limit=1
        )
        if overtime_setting:
            value = {
                "name": _("Overtime setting"),
                "view_type": "form",
                "view_mode": "form",
                "res_model": "hr.overtime.setting",
                "view_id": False,
                "type": "ir.actions.act_window",
                "res_id": overtime_setting.id,
            }
            return value
