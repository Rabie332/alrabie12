from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ClearanceRequest(models.Model):
    _inherit = "clearance.request"



    @api.depends('sale_ids')
    def _compute_sales(self):
        """Calculate sales number based on the same customer."""
        for record in self:
            sales_count = self.env['sale.order'].search_count([
                ('partner_id', '=', record.partner_id.id)  # Filter by the same partner_id
            ])
            record.sales_number = sales_count
            
            
    def sales_tree_view(self):
        """Get sales for this object with the same customer."""
        action = self.env.ref("sale.action_orders").sudo().read()[0]
        # Update the domain to filter sales orders by the partner_id of the clearance request
        action["domain"] = [
            ("partner_id", "=", self.partner_id.id),  # Filter by the same partner_id
        ]
        action["context"] = {
            "default_clearance_request_id": self.id,
            "clearance_request_state": self.state,
            "default_partner_id": self.partner_id.id,
        }
        return action
    
    
class ClearanceRequestShipmentRoute(models.Model):
    _name = "clearance.request.shipment.route"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Clearance Request Shipment Route"

    name = fields.Char(string="Name", readonly=0, tracking=True,)
    shipment_from = fields.Char(string="From", required=1, translate=1, tracking=True,)
    shipment_to = fields.Char(string="To", required=1, translate=1, tracking=True,)
    currency_id = fields.Many2one(
        "res.currency",
        "Currency",
        required=True,
        default=lambda self: self.env.company.currency_id.id,
        tracking=True,
    )
    container_transport = fields.Monetary("Container transport", tracking=True,)
    parcel_transport = fields.Monetary("Parcel transport ", tracking=True,)
    minimum_amount = fields.Monetary("Minimum Amount", tracking=True,)
    active = fields.Boolean(default=True, string="Active", tracking=True,)
    company_id = fields.Many2one(
        "res.company",
        "Company",
        default=lambda self: self.env.company,
        tracking=True,
    )
    product_id = fields.Many2one("product.product", string="Product", tracking=True,)
    transport_type = fields.Selection(
        string="Transport type",
        selection=[
            ("warehouse", "Yard"),
            ("customer", "Customer site"),
            ("other", "Other site"),
            ("empty", "Return empty"),
        ],
        tracking=True,
    )
    line_ids = fields.One2many(
        "clearance.request.shipment.route.line",
        "route_id",
        string="Route Amounts",
    )
    line_price_ids = fields.One2many(
        "clearance.request.shipment.route.price",
        "route_id",
        string="Route Prices",
    )

    @api.model
    def create(self, values):
        route = super(ClearanceRequestShipmentRoute, self).create(values)
        if route:
            route.name = str(route.shipment_from) + "-" + str(route.shipment_to)
        return route

    def write(self, vals):
        route = super(ClearanceRequestShipmentRoute, self).write(vals)
        if vals.get("shipment_from", False) or vals.get("shipment_to", False):
            self.name = str(self.shipment_from) + "-" + str(self.shipment_to)
        return route

