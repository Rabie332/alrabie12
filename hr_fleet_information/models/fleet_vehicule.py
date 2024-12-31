from odoo import fields, models


class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    periodic_inspection_number = fields.Char(string="Periodic inspection Number", tracking=True,)
    periodic_inspection_end_date = fields.Date(
        string="Periodic inspection Expiration Date"
    , tracking=True,)
    driving_license_number = fields.Char(string="Driving License Number", tracking=True,)
    driving_license_end_date = fields.Date(string="Driving License Expiration Date", tracking=True,)
    port_permit_number = fields.Char(string="Port Permit Number", tracking=True,)
    port_permit_end_date = fields.Date(string="Port Permit Expiration Date", tracking=True,)
    play_card_number = fields.Char(string="Play Card Number", tracking=True,)
    play_card_end_date = fields.Date(string="Play Card Expiration Date", tracking=True,)
    expiry_card_number = fields.Char(string="Expiry Card Number", tracking=True,)
    expiry_card_end_date = fields.Date(string="Expiry Card Expiration Date", tracking=True,)
    insurance_number = fields.Char(string="Insurance  Number", tracking=True,)
    insurance_end_date = fields.Date(string="Insurance Expiration Date", tracking=True,)
    expiry_card_number = fields.Char(string="Expiry Card Number", tracking=True,)
    expiry_card_end_date = fields.Date(string="Expiry Card Expiration Date", tracking=True,)
    insurance_no_cargo = fields.Char("Insurance No/Cargo", tracking=True,)
    insurance_no_cargo_end_date = fields.Date("Insurance No/Cargo End Date", tracking=True,)
    driver_license_expiry_date = fields.Date(string="Driver License Expiry Date", tracking=True,)
    driver_expiry_date = fields.Date(string="Driver Expiry Date", tracking=True,)
