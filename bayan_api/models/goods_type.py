from odoo import fields, api, _, models


class GoodsType(models.Model):
  _name = "goods.type"
  _description = 'Goods Type'
  _rec_name = "name_arabic"
  
  goods_id_bayan = fields.Integer(string="ID")
  name_english = fields.Char(string="English Name")
  name_arabic = fields.Char(string="Arabic Name")