from datetime import datetime

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"

    document_ids = fields.One2many(
        "ir.attachment",
        compute="_compute_document_ids",
        groups="hr.group_hr_user",
        string="Documents",
    )
    documents_count = fields.Integer(
        compute="_compute_document_ids",
        groups="hr.group_hr_user",
        string="Document Count",
    )
    is_guest = fields.Boolean(string="Guest")
    guest_type = fields.Selection(
        [
            ("citizen", "Citizen"),
            ("resident", "Resident"),
            ("gulf_citizen", "Gulf citizen"),
            ("visitor", "Visitor"),
        ],
        string="Guest Type",
    )
    identification_id = fields.Char(string="Identification ID")
    visa_number = fields.Char(string="Visa Number")
    card_number = fields.Char(string="Card number")
    residence_number = fields.Char(string="Residence number")
    passport_id = fields.Char(string="Passport ID")
    gender = fields.Selection(
        [("unknown ", "Unknown"), ("male", "Male"), ("female", "Female")],
        string="Gender",
    )
    birthday = fields.Date(string="Birthday")
    last_room_id = fields.Many2one(
        "hotel.room",
    )
    reservation_ids = fields.One2many(
        "hotel.reservation",
        "partner_id",
        compute="_compute_reservation_ids",
        string="Reservations",
    )
    reservation_count = fields.Integer(
        compute="_compute_reservation_ids",
        string="Reservation Count",
    )
    age_group = fields.Selection(
        [
            ("undefined", "Undefined"),
            ("adult", "Adult"),
            ("child", "Child"),
        ],
        string="Age Group",
        compute="_compute_age_group",
        store=1,
    )
    nationality_id = fields.Many2one("res.country", string="Nationality")

    @api.model
    def create(self, vals):
        if not vals.get("gender") and vals.get("is_guest"):
            raise ValidationError(_("You should add gender for guest"))
        return super(ResPartner, self).create(vals)

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        """Search in number,display_name,identification_id."""
        args = args or []
        recs = self.browse()
        if name:
            domain = [
                "|",
                "|",
                "|",
                "|",
                "|",
                ("name", operator, name),
                ("identification_id", operator, name),
                ("residence_number", operator, name),
                ("visa_number", operator, name),
                ("card_number", operator, name),
                ("mobile", operator, name),
            ]

            recs = self.search(domain + args, limit=limit)
        if not recs:
            recs = self.search([("name", operator, name)] + args, limit=limit)
        return recs.name_get()

    @api.depends("birthday")
    def _compute_age_group(self):
        for guest in self:
            guest.age_group = "undefined"
            today = datetime.today().date()
            if guest.birthday:
                guest.age_group = "adult"
                age = (today - guest.birthday).days / 354
                if age <= 12:
                    guest.age_group = "child"

    def _compute_document_ids(self):
        attachments = self.env["ir.attachment"].search(
            [("res_model", "=", self._name), ("res_id", "in", self.ids)]
        )

        result = dict.fromkeys(self.ids, self.env["ir.attachment"])
        for attachment in attachments:
            result[attachment.res_id] |= attachment

        for employee in self:
            employee.document_ids = result[employee.id]
            employee.documents_count = len(employee.document_ids)

    def action_get_attachment_tree_view(self):
        action = self.env.ref("base.action_attachment").read()[0]
        action["context"] = {
            "default_res_model": self._name,
            "default_res_id": self.ids[0],
        }
        action["domain"] = str(
            [("res_model", "=", self._name), ("res_id", "in", self.ids)]
        )
        action["search_view_id"] = (
            self.env.ref("hotel_customer.ir_attachment_view_search").id,
        )
        return action

    def _compute_reservation_ids(self):
        for rec in self:
            reservations_individual = rec.env["hotel.reservation"].search(
                [("partner_id", "=", rec.id), ("reservation_type", "=", "individual")]
            )
            reservations_collective = (
                rec.env["hotel.reservation.line"]
                .search(
                    [
                        "|",
                        "&",
                        ("tenant", "=", "person"),
                        ("partner_id", "=", rec.id),
                        "&",
                        ("tenant", "=", "company"),
                        ("partner_company_id", "=", rec.id),
                    ]
                )
                .mapped("line_id")
            )
            reservations = list(
                set(reservations_individual.ids + reservations_collective.ids)
            )
            rec.reservation_count = len(reservations)
            rec.reservation_ids = [(6, 0, reservations)]

    def action_get_reservation_tree_view(self):
        return {
            "name": _("Reservation"),
            "type": "ir.actions.act_window",
            "view_mode": "tree,form",
            "res_model": "hotel.reservation",
            "domain": [("id", "in", self.reservation_ids.ids)],
        }

    @api.onchange("guest_type")
    def _onchange_guest_type(self):
        self.passport_id = (
            self.identification_id
        ) = self.residence_number = self.card_number = False


class HotelLostFound(models.Model):
    _inherit = "hotel.lost.found"

    partner_id = fields.Many2one(domain="[('is_guest', '=', True)]")
