from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    fleet_maintenance_ids = fields.One2many(
        "fleet.maintenance",
        "vehicle_id",
        string="Maintenance",
    )
    maintenance_count = fields.Integer(
        compute="_compute_count_all", string="Maintenance Count"
    )

    def _compute_count_all(self):
        for vehicle in self:
            super(FleetVehicle, vehicle)._compute_count_all()
            vehicle.maintenance_count = len(vehicle.fleet_maintenance_ids)


class FleetMaintenance(models.Model):
    _name = "fleet.maintenance"
    _description = "Fleet Maintenance"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    def _default_odometer(self):
        return (
            self.env["fleet.vehicle"]
            .search([("id", "=", self._context.get("active_id"))], limit=1)
            .odometer
        )

    name = fields.Char(
        string="Name",
        readonly=True,
        states={"draft": [("readonly", False)]},
        required=True,
    )
    maintenance_type = fields.Selection(
        string="Maintenance Type",
        selection=[("preventive", "Preventive"), ("corrective", "Corrective")],
        default="preventive",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    odometer = fields.Float(
        string="Odometer Value",
        default=_default_odometer,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    odometer_unit = fields.Selection(related="vehicle_id.odometer_unit", string="Unit")
    vehicle_type = fields.Selection(related="vehicle_id.vehicle_type")
    company_id = fields.Many2one(
        "res.company",
        "Company",
        default=lambda self: self.env.company,
        readonly=True,
        states={"draft": [("readonly", False)]},
        required=1,
    )
    warehouse_id = fields.Many2one(
        "stock.warehouse",
        string="Warehouse",
        readonly=True,
        states={"draft": [("readonly", False)]},
        required=True,
    )
    location_id = fields.Many2one(
        "stock.location",
        string="Location",
        domain="[('id', 'in', location_ids)]",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    location_ids = fields.Many2many(
        "stock.location", string="Locations", compute="_compute_locations", store=1
    )
    product_ids = fields.Many2many(
        "product.product", string="Products", compute="_compute_products", store=1
    )

    product_id = fields.Many2one(
        "product.product",
        "Product",
        domain="[('id', 'in', product_ids)]",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    product_tmpl_id = fields.Many2one(
        "product.template",
        string="Product Template",
        related="product_id.product_tmpl_id",
        readonly=False,
    )
    product_qty = fields.Float(
        "Quantity",
        digits="Product Unit of Measure",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    product_uom = fields.Many2one("uom.uom", "UoM", related="product_id.uom_id")
    employee_id = fields.Many2one(
        "hr.employee",
        string="Technician name",
        required=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("audit", "Audit"),
            ("progress", "Progress"),
            ("done", "Done"),
            ("cancel", "Cancelled"),
        ],
        default="draft",
        string="Status",
        tracking=True,
    )
    vehicle_id = fields.Many2one("fleet.vehicle", string="Vehicle")
    description = fields.Text(
        "Notes", readonly=True, states={"draft": [("readonly", False)]}
    )
    picking_id = fields.Many2one("stock.picking", string="Picking")
    next_maintenance_date = fields.Date(
        string="Next Maintenance",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    unit = fields.Char(
        string="Unit", readonly=True, states={"draft": [("readonly", False)]}
    )
    engineer_report = fields.Html(
        string="Engineer Report",
        readonly=True,
        states={"draft": [("readonly", False)], "audit": [("readonly", False)]},
    )

    def _create_picking_maintenance(self):

        vals_picking = {
            "picking_type_id": self.warehouse_id.out_type_id.id,
            "location_id": self.location_id.id,
            "location_dest_id": self.env.ref("stock.stock_location_customers").id,
            "company_id": self.company_id.id,
            "origin": self.name,
            "move_ids_without_package": [
                (
                    0,
                    0,
                    {
                        "name": self.name,
                        "product_id": self.product_id.id,
                        "product_uom_qty": self.product_qty,
                        "product_uom": self.product_uom.id,
                        "location_id": self.location_id.id,
                        "location_dest_id": self.env.ref(
                            "stock.stock_location_customers"
                        ).id,
                        "company_id": self.company_id.id,
                    },
                ),
            ],
        }
        picking = self.env["stock.picking"].create(vals_picking)
        picking.action_confirm()
        picking.action_assign()
        for move_line in picking.move_ids_without_package[0].move_line_ids:
            move_line.qty_done = self.product_qty
        picking.button_validate()
        self.picking_id = picking.id

    @api.depends("warehouse_id")
    def _compute_locations(self):
        for maintenance in self:
            maintenance.location_ids = (
                maintenance.env["stock.location"]
                .search(
                    [
                        (
                            "id",
                            "child_of",
                            maintenance.warehouse_id.view_location_id.id,
                        ),
                        ("usage", "=", "internal"),
                    ]
                )
                .ids
            )

    @api.depends("location_id")
    def _compute_products(self):
        for maintenance in self:
            maintenance.product_ids = (
                maintenance.env["stock.quant"]
                .search([("location_id", "=", maintenance.location_id.id)])
                .mapped("product_id")
                .ids
            )

    @api.constrains("product_qty")
    def check_product_qty(self):
        for maintenance in self:
            if not maintenance.product_qty:
                raise ValidationError(_("The Quantity must be greater than zero"))
            free_qty = maintenance.product_id.with_context(
                location=maintenance.location_id.id
            ).free_qty
            if maintenance.product_qty > free_qty:
                raise ValidationError(
                    _("Product %s not available. You can only request %s")
                    % (maintenance.product_id.name, free_qty)
                )

    def action_audit(self):
        for maintenance in self:
            maintenance.state = "audit"

    def action_progress(self):
        for maintenance in self:
            maintenance.state = "progress"

    def action_done(self):
        for maintenance in self:
            maintenance.state = "done"
            maintenance._create_picking_maintenance()

    def action_cancel(self):
        for maintenance in self:
            maintenance.state = "cancel"
