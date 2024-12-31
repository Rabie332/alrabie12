from odoo import _, models


class HotelRoom(models.Model):

    _inherit = "hotel.room"

    def button_maintenance(self):
        context = {
            "default_type": "maintenance",
            "default_room_id": self.id,
            "default_categ_id": self.room_categ_id.id,
        }
        if self.floor_id.inspector_id:
            context.update({"default_inspector_id": self.floor_id.inspector_id.id})
        return {
            "name": _("Housekeeping Services Maintenance"),
            "res_model": "hotel.housekeeping",
            "view_mode": "form",
            "type": "ir.actions.act_window",
            "context": context,
            "target": "current",
        }
