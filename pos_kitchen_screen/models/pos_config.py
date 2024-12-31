from odoo import _, models


class PosConfig(models.Model):
    _inherit = "pos.config"

    def open_kitchen_screen(self):
        """Open kitchen screen orders in kanban view"""
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "point_of_sale.action_pos_order_filtered"
        )
        action["display_name"] = _("Kitchen Screen")
        action["views"] = [
            (
                self.env.ref("pos_kitchen_screen.pos_order_view_kanban_kitchen").id,
                "kanban",
            )
        ]
        return action
