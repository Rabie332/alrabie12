from odoo import fields, models


class HotelLostFound(models.Model):
    _name = "hotel.verification"
    _description = "Hotel verification"

    type = fields.Selection(
        [("day", "Day"), ("night", "Night")], string="Type", required=True
    )
    date = fields.Date("Date", required=True, default=fields.Datetime.now)
    notes = fields.Text(string="Notes", required=True)
    verifier_id = fields.Many2one("res.users", "Verifier", required=True)

    def name_get(self):
        result = []
        for verification in self:
            name = str(verification.verifier_id.name)
            if verification.verifier_id:
                name = " - ".join([str(verification.date), name])
            result.append((verification.id, name))
        return result
