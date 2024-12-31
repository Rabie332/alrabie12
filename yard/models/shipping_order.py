from odoo import _, api, fields, models


class ShippingOrder(models.Model):
    _inherit = "shipping.order"

    return_yard = fields.Selection(
        [
            ('empty_to_yard', 'Empty to Yard'),
            ('empty_to_shipping_agent', 'Empty to Shipping Agent')
        ],
        required=True,
        string="Return Option"
    )

    is_damm = fields.Boolean(
        compute="_compute_is_damm", store=True)

    @api.depends('company_id')
    def _compute_is_damm(self):
        dammam_name_id = ['Farha Logistic Dammam', 'فرحه لوجستك الدمام']
        for record in self:
            if record.company_id.name in dammam_name_id:
                record.is_damm = True
            else:
                record.is_damm = False


class ShippingOrderLine(models.Model):
    _inherit = "shipping.order.line"

    zone_id = fields.Many2one('yard.zone', string="Zone")
    container_id = fields.Many2one(
        'yard.container',
        string="Storage Address",
    )
    shipment_type_size_id = fields.Many2one(
        "clearance.shipment.type.size", string="Size"
    )
    shipping_order_id = fields.Many2one(
        'shipping.order', string="Shipping Order")
    transport_type = fields.Selection(
        related='shipping_order_id.transport_type', string="Transport Type")
    display_yard_fields = fields.Boolean(
        default=False, compute="_compute_display_yard_fields")

    goods_id = fields.Many2one(
        "clearance.request.shipment.type", string="Good")

    @api.onchange('shipment_type_size_id', 'shipping_order_id')
    def _onchange_shipment_type_size_id(self):
        domain = []
        if self.shipment_type_size_id and self.shipping_order_id:
            size_name = self.shipment_type_size_id.name
            transport_type = self.shipping_order_id.transport_type
            if size_name == "20FT":
                if transport_type == 'empty':
                    domain = [('zone_type', '=', '20E')]
                else:
                    domain = ['|', '|',
                              ('zone_type', '=', '20'),
                              ('zone_type', '=', '20Mix'),
                              ('zone_type', '=', '20S')]
            elif size_name == "40FT":
                if transport_type == 'empty':
                    domain = [('zone_type', '=', '40E')]
                else:
                    domain = ['|', '|',
                              ('zone_type', '=', '40'),
                              ('zone_type', '=', '40Mix'),
                              ('zone_type', '=', '40S')]
            else:
                domain = []

        return {'domain': {'zone_id': domain, 'container_id': "[('zone_id', '=', zone_id), ('state', '=', 'available')]"}}

    @api.depends('shipping_order_id')
    def _compute_display_yard_fields(self):
        for record in self:
            record.display_yard_fields = record.shipping_order_id.transport_type == "warehouse"

    @api.onchange('zone_id')
    def _onchange_zone_id(self):
        self.container_id = False

    @api.model
    def create(self, vals):
        record = super().create(vals)
        if record.shipping_order_id.transport_type == "customer":
            # Unlink any containers associated with this shipping order line
            containers = self.env['yard.container'].search(
                [('occupied_by.goods_id', '=', record.goods_id.id)], limit=1)
            containers.write({
                'occupied_by': False,
                'is_occupied': False,
                'state': 'available'
            })
        elif record.container_id:
            record.container_id.write({
                'occupied_by': record.id,
                'is_occupied': True,
                'state': 'occupied'
            })
        return record

    def unlink(self):
        for record in self:
            if record.container_id:
                record.container_id.write({
                    'occupied_by': False,
                    'is_occupied': False,
                    'state': 'available'
                })
        return super().unlink()
