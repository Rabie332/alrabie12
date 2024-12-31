from odoo import api, fields, models


class ResPartnerClearanceRoute(models.Model):
    _name = "res.partner.clearance.route"
    _description = "Partner Clearance Route"

    # ------------------------------------------------------
    # Fields
    # ------------------------------------------------------

    transport_type = fields.Selection(
        string="Transport type",
        selection=[
            ("warehouse", "Yard"),
            ("customer", "Customer site"),
            ("other", "Other site"),
            ("empty", "Return empty"),
        ],
        required=1,
        default="warehouse",
    )

    route_id = fields.Many2one(
        "clearance.request.shipment.route", string="Route", required=1
    )
    route_from = fields.Char(string="From", readonly=1)
    route_to = fields.Char(string="To", readonly=1)
    partner_id = fields.Many2one("res.partner", string="Partner")
    company_id = fields.Many2one(
        "res.company",
        "Company",
    )

    # ------------------------------------------------------
    # Onchange Method
    # ------------------------------------------------------

    @api.onchange("route_id")
    def _onchange_route_id(self):
        """Set route_from and route_to by default as selected Route"""
        if self.route_id:
            self.route_from = self.route_id.shipment_from
            self.route_to = self.route_id.shipment_to
            self.company_id = self.route_id.company_id.id
