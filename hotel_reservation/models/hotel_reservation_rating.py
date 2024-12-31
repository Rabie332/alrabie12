from odoo import _, fields, models


class HotelReservationEvaluation(models.Model):

    _name = "hotel.reservation.rating"
    _description = "Reservation Rating"

    name = fields.Char(string="Name", translate=1)
    satisfaction_percentage = fields.Float(
        string="Satisfaction", compute="_compute_rating"
    )
    dissatisfaction_percentage = fields.Float(
        string="Dissatisfaction", compute="_compute_rating"
    )
    highly_dissatisfaction_percentage = fields.Float(
        string="Highly dissatisfaction", compute="_compute_rating"
    )
    no_rating_percentage = fields.Float(string="No rating", compute="_compute_rating")
    company_id = fields.Many2one(
        "res.company", string="Company", default=lambda self: self.env.company
    )
    rating_ids = fields.Many2many("rating.rating", string="Ratings Details")

    def _compute_rating(self):
        """Calculate ratings(satisfied, no_satisfied, dissatisfied)"""
        for rating in self:
            rating_obj = rating.env["rating.rating"]
            rating.satisfaction_percentage = (
                rating.dissatisfaction_percentage
            ) = rating.highly_dissatisfaction_percentage = rating.no_rating_percentage
            domain = [("res_model", "=", "hotel.reservation")]
            rating_satisfied = rating_obj.search_count(
                [
                    ("rating_text", "=", "satisfied"),
                ]
                + domain
            )
            rating_not_satisfied = rating_obj.search_count(
                [
                    ("rating_text", "=", "not_satisfied"),
                ]
                + domain
            )
            rating_highly_dissatisfied = rating_obj.search_count(
                [
                    ("rating_text", "=", "highly_dissatisfied"),
                ]
                + domain
            )
            rating_no_rating = rating_obj.search_count(
                [
                    ("rating_text", "=", "no_rating"),
                ]
                + domain
            )
            all_rating = (
                rating_satisfied
                + rating_not_satisfied
                + rating_highly_dissatisfied
                + rating_no_rating
            )
            # calculate ratings
            if all_rating:
                rating.satisfaction_percentage = (rating_satisfied / all_rating) * 100
                rating.dissatisfaction_percentage = (
                    rating_not_satisfied / all_rating
                ) * 100
                rating.highly_dissatisfaction_percentage = (
                    rating_highly_dissatisfied / all_rating
                ) * 100
                rating.no_rating_percentage = (rating_no_rating / all_rating) * 100

    def button_rating_details(self):
        """Open Ratings  Details."""
        view_id = self.env.ref(
            "hotel_reservation.hotel_reservation_rating_view_tree"
        ).id
        domain = [("res_model", "=", "hotel.reservation")]
        if self._context.get("default_rating") == "satisfaction":
            domain.append(("rating_text", "=", "satisfied"))
        if self._context.get("default_rating") == "not_satisfied":
            domain.append(("rating_text", "=", "not_satisfied"))
        if self._context.get("default_rating") == "dissatisfied":
            domain.append(("rating_text", "=", "highly_dissatisfied"))
        if self._context.get("default_rating") == "no_rating":
            domain.append(("rating_text", "=", "no_rating"))

        return {
            "name": _("Details"),
            "view_mode": "tree",
            "views": [(view_id, "tree")],
            "res_model": "rating.rating",
            "view_id": view_id,
            "type": "ir.actions.act_window",
            "res_id": False,
            "target": "current",
            "domain": domain,
        }
