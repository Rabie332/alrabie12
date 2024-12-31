from odoo import api, fields, models


class HotelLostFound(models.Model):
    _name = "hotel.lost.found"
    _description = "Hotel Lost and found"

    room_id = fields.Many2one("hotel.room", "Room")
    partner_id = fields.Many2one(
        "res.partner",
        "Guest",
    )
    type = fields.Selection(
        [("lost", "Lost"), ("found", "Found")], string="Type", required=True
    )
    found_date = fields.Datetime("Found date")
    delivery_date = fields.Datetime("Delivery date")
    description = fields.Text(string="Description", required=True)
    founder = fields.Char(string="Founder")
    name = fields.Char("Number", readonly=True)
    company_id = fields.Many2one(
        "res.company", string="Hotel", default=lambda self: self.env.company
    )
    active = fields.Boolean(default=True)
    delivered = fields.Boolean(string="Delivered")

    @api.model
    def create(self, values):
        """Generate sequence based on type ."""
        res = super(HotelLostFound, self).create(values)
        sequence = (
            "hotel.lost.sequence" if res.type == "lost" else "hotel.found.sequence"
        )
        res.name = res.env["ir.sequence"].next_by_code(sequence)
        return res
