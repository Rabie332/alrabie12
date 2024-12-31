from odoo import _, models


class ResUsers(models.Model):
    _inherit = "res.users"

    def _compute_can_edit(self):
        can_edit = self.env["ir.config_parameter"].sudo().get_param(
            "hr.hr_employee_self_edit"
        ) or self.env.user.has_group("hr.group_hr_manager")
        for user in self:
            user.can_edit = can_edit

    def get_my_profile(self):
        """Show view form for My Profile.
        :return: Dictionary contain view form of res.users
        """
        return {
            "name": _("My Profile"),
            "view_type": "form",
            "view_mode": "form",
            "res_model": "res.users",
            "view_id": self.env.ref("hr.res_users_view_form_profile").id,
            "type": "ir.actions.act_window",
            "res_id": self.env.user.id,
        }
