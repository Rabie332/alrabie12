from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PriceSetting(models.Model):
    _name = "price.setting"
    _description = "Price Setting"

    room_type_id = fields.Many2one("hotel.room.type", string="Room Type", required=1)
    date_from = fields.Date(string="Date From", required=1)
    date_to = fields.Date(string="Date To", required=1)
    addition_type = fields.Selection(
        [("percentage", "Percentage"), ("fixed", "Fixed Amount")],
        default="percentage",
        string="Addition Type",
    )
    amount = fields.Float(string="Amount", required=1)
    company_id = fields.Many2one(
        "res.company", string="Company", default=lambda self: self.env.company
    )

    @api.constrains("room_type_id", "date_from", "date_to", "company_id")
    def _check_intersection(self):
        """Verify date from and to and  intersection."""
        for setting in self:
            if setting.date_to and setting.date_from:
                # Verify Date to and Date FRom
                if setting.date_to < setting.date_from:
                    raise ValidationError(
                        _("Date to should be greater or equal to date From")
                    )
                # Check Intersection setting price
                if setting.room_type_id:
                    for rec in setting.search(
                        [
                            ("room_type_id", "=", setting.room_type_id.id),
                            ("company_id", "=", setting.company_id.id),
                            ("id", "!=", setting.id),
                        ]
                    ):
                        if (
                            rec.date_from <= setting.date_from <= rec.date_to
                            or rec.date_from <= setting.date_to <= rec.date_to
                            or setting.date_from <= rec.date_from <= setting.date_to
                            or setting.date_from <= rec.date_to <= setting.date_to
                        ):
                            raise ValidationError(
                                _("There is an overlap in the dates of Price Setting")
                            )
