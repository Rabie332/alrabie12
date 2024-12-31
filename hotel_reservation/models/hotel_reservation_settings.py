from odoo import fields, models


class HotelReservationSource(models.Model):

    _name = "hotel.reservation.source"
    _description = "Reservation Source"

    name = fields.Char(string="Name", translate=1, required=1)
    active = fields.Boolean(string="Active", default=True)


class ReservationVisitReason(models.Model):

    _name = "reservation.visit.reason"
    _description = "Visit Reasons"

    name = fields.Char(string="Name", translate=1, required=1)
    active = fields.Boolean(string="Active", default=True)


class ReservationCondition(models.Model):

    _name = "reservation.condition"
    _description = "Reservation Condition"
    _rec_name = "company_id"

    conditions = fields.Text(string="Condition", translate=1, required=True)
    active = fields.Boolean(string="Active", default=True)
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )
