from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    transport_driver_card_number = fields.Char(
        string="Transport Authority driver card number"
    )
    expiration_date_authority_card = fields.Date(
        string="Expiration date transportation authority card"
    )
    odometer_unit = fields.Selection(
        selection_add=[
            ("hours", "Hours"),
        ],
        ondelete={
            "hours": "cascade",
        },
    )

    @api.constrains("license_plate")
    def _check_license_plate(self):
        for record in self:
            license_plate_ids = record.search(
                [("id", "!=", record.id), ("license_plate", "=", record.license_plate)]
            )
            if license_plate_ids:
                raise ValidationError(
                    _("The plate number already exists %s.", record.license_plate)
                )


class ShippingOrderLine(models.Model):
    _inherit = "shipping.order.line"

    def print_way_bill_report(self):
        self.ensure_one()
        if self.vehicle_id:
            message = _("Expiration date transportation authority card")
            self.check_date_fleet(
                self.vehicle_id.expiration_date_authority_card, message
            )
        return super(ShippingOrderLine, self).print_way_bill_report()
