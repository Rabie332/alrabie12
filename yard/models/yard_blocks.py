from odoo import models, fields


class YardBlocks(models.Model):
    _name = 'yard.blocks'
    _description = 'Yard Blocks'

    name = fields.Char(string="Name", required=True)
    item_type = fields.Selection([
        ('Bulk Store', 'Bulk Store'),
        ('Goods Equipments', 'Goods Equipments'),
        ('Company Trucks', 'Company Trucks')
    ], string="Type of Block")

    bulk_ids = fields.One2many(
        'yard.block.line', 'yard_block_id', string="Bulk Items",
        domain=[('item_type', '=', 'Bulk Store')])
    equipment_ids = fields.One2many(
        'yard.block.line', 'yard_block_id', string="Equipment Items",
        domain=[('item_type', '=', 'Goods Equipments')])
    trucks_ids = fields.One2many(
        'yard.truck.line', 'yard_block_id', string="Trucks")


class YardBlockLine(models.Model):
    _name = 'yard.block.line'
    _description = 'Yard Block Line'

    yard_block_id = fields.Many2one(
        'yard.blocks', string="Yard Block", required=True, ondelete='cascade')
    item_type = fields.Selection([
        ('Bulk Store', 'Bulk Store'),
        ('Goods Equipments', 'Goods Equipments')
    ], string="Item Type", required=True)
    product_id = fields.Many2one(
        'product.template', string="Product", required=True)
    product_name = fields.Char(
        related='product_id.name', string="Product Name", readonly=True)
    product_price = fields.Float(
        related='product_id.list_price', string="Price", readonly=True)


class YardTruckLine(models.Model):
    _name = 'yard.truck.line'
    _description = 'Yard Truck Line'

    yard_block_id = fields.Many2one(
        'yard.blocks', string="Yard Block", required=True, ondelete='cascade')
    truck_id = fields.Many2one(
        'fleet.vehicle', string="Truck", required=True)
    truck_name = fields.Char(
        related='truck_id.name', string="Truck Name", readonly=True)
