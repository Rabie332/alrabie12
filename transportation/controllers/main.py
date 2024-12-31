from odoo import http
from odoo.http import request
from odoo.tools.translate import _


class Rating(http.Controller):
    @http.route(
        "/rating/clearance/<string:token>/<int:rate>", type="http", auth="public"
    )
    def open_rating(self, token, rate, **kwargs):
        """Open rating clearance"""
        assert rate in (1, 3, 5), "Incorrect rating"
        rating = (
            request.env["rating.rating"].sudo().search([("access_token", "=", token)])
        )
        if not rating:
            return request.not_found()
        rate_names = {
            1: _("highly dissatisfied"),
            3: _("not satisfied"),
            5: _("satisfied"),
        }
        rating.write({"rating": rate, "consumed": True})
        lang = rating.partner_id.lang or "en_US"
        return (
            request.env["ir.ui.view"]
            .with_context(lang=lang)
            ._render_template(
                "transportation.rating_page_transportation_submit",
                {
                    "rating": rating,
                    "token": token,
                    "rate_names": rate_names,
                    "rate": rate,
                },
            )
        )

    @http.route(
        ["/rating/clearance/<string:token>/<int:rate>/submit_feedback"],
        type="http",
        auth="public",
        methods=["post"],
    )
    def submit_rating(self, token, rate, **kwargs):
        """Submit rating clearance."""
        rating = (
            request.env["rating.rating"].sudo().search([("access_token", "=", token)])
        )

        record_sudo = request.env[rating.res_model].sudo().browse(rating.res_id)
        record_sudo.rating_apply(rate, token=token, feedback=kwargs.get("feedback"))
        lang = rating.partner_id.lang or "en_US"
        return (
            request.env["ir.ui.view"]
            .with_context(lang=lang)
            ._render_template(
                "transportation.rating_external_transportation_page_view",
                {
                    "web_base_url": request.env["ir.config_parameter"]
                    .sudo()
                    .get_param("web.base.url"),
                    "rating": rating,
                },
            )
        )
