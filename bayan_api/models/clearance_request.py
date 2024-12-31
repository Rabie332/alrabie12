from lxml import etree

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

# shipment_type_line_ids.weight

    
class ClearanceRequest(models.Model):
    _inherit = "clearance.request"
    
    shipment_type_line_ids = fields.One2many(
        "clearance.request.shipment.type",
        "clearance_request_id",
        string="Lines",
        readonly=True,
        states={
            "draft": [("readonly", False)],
            "customs_clearance": [("readonly", False)],
            "transport": [("readonly", False)],
            "delivery": [("readonly", False)],
        },
    )
    
     # New computed field to check if user is in specific group
    is_transportation_responsible = fields.Boolean(compute='_compute_is_transportation_responsible', string='Is Transportation Responsible')

    @api.depends('create_uid', 'create_uid.groups_id')
    def _compute_is_transportation_responsible(self):
        transportation_group = self.env.ref('transportation.group_transportation_responsible')
        for record in self:
            record.is_transportation_responsible = transportation_group in self.env.user.groups_id        
            
    def update_goods_type_for_all_lines(self):
        # Assuming this method is triggered by a button in your view
        if self.shipment_type_line_ids:
            first_line_goods_type = self.shipment_type_line_ids[0].goods_type_bayan
            first_line_container_category = self.shipment_type_line_ids[0].container_category_id
            first_line_shipment_type_size = self.shipment_type_line_ids[0].shipment_type_size_id
            first_line_weight = self.shipment_type_line_ids[0].weight
            for line in self.shipment_type_line_ids:
                line.goods_type_bayan = first_line_goods_type
                line.container_category_id = first_line_container_category
                line.shipment_type_size_id = first_line_shipment_type_size
                line.weight = first_line_weight

    def action_send(self):
        # Your custom validation or logic before the original logic
        for request in self:
            if request.request_type in ["transport", "storage", "other_service"]:
                for shipment_type_line in request.shipment_type_line_ids:
                    if not shipment_type_line.goods_type_bayan:
                        raise ValidationError(_("You must fill Bayan Goods Type for all shipment type lines."))
        
        # Call the original logic
        super(ClearanceRequest, self).action_send()
        
    def action_customs_statement(self):
        # Your custom validation or logic before the original logic
        for request in self:
            for shipment_type_line in request.shipment_type_line_ids:
                if not shipment_type_line.goods_type_bayan:
                    raise ValidationError(_("You must fill Bayan Goods Type for all shipment type lines."))
        
        # Call the original logic
        super(ClearanceRequest, self).action_customs_statement()
        
        
class ClearanceRequestShipmentType(models.Model):
    _inherit = "clearance.request.shipment.type"
   
    goods_type_bayan = fields.Many2one('goods.type', string='Arabic Name')

class ClearanceRequestShipmentRoute(models.Model):
    _inherit = "clearance.request.shipment.route"
    
    bayan_route_from = fields.Char("From")
    bayan_route_to = fields.Char("To")
    
    bayan_route_from_id = fields.Integer("From ID")
    bayan_route_to_id = fields.Integer("To ID")
    
    