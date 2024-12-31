from odoo import _, models


class PosConfig(models.Model):
    _inherit = "pos.config"

    def open_services_screen(self):
        """Open service screen orders in kanban view"""
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "pos_pay_later_stages.action_pos_service_filtered"
        )
        action["display_name"] = _("Services Screen")
        action["views"] = [
            (
                self.env.ref("pos_pay_later_stages.pos_service_view_kanban_service").id,
                "kanban",
            )
        ]
        return action
