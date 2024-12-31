from odoo import fields, models


class HotelRoom(models.Model):

    _inherit = "hotel.room"

    is_send_mail_dirty = fields.Boolean(string="Send mail Dirty")
    is_send_mail_maintenance = fields.Boolean(string="Send mail Maintenance")

    def write(self, vals):
        """
        Overrides orm write method.
        @param self: The object pointer
        @param vals: dictionary of fields value.
        """
        if "status" in vals and vals.get("status") != "maintenance":
            self.is_send_mail_maintenance = False
        if "is_clean" in vals and not vals.get("is_clean"):
            self.is_send_mail_dirty = False

        return super(HotelRoom, self).write(vals)
