# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
from odoo import api, fields, models
from datetime import datetime



class PosOrder(models.Model):
    """
    Extends 'pos.order' model to add custom fields and methods for invoice
    generation.
    """
    _inherit = 'pos.order'

    sale_barcode = fields.Char(string='Sale Barcode',
                               help='Barcode associated with the sale.')
    # year = fields.Char(string='Year', default=lambda self: str(datetime.now().year))


    # def get_receipt_render_env(self):
    #         receipt = super(PosOrder, self).get_receipt_render_env()
    #         receipt['year'] = self.year
    #         return receipt



    # @api.model
    # def _process_order(self, order_data, draft, existing_order):
    #     # Call the original _process_order and get the order ID
    #     order_id = super(PosOrder, self)._process_order(order_data, draft, existing_order)
        
    #     # Retrieve the created pos.order record
    #     pos_order = self.browse(order_id)
        
    #     # Add the current year to the order name
    #     current_year = datetime.now().year
    #     if pos_order.name:
    #         pos_order.name = f"{pos_order.name}/{current_year}"
        
    #     return order_id

    # @api.model
    # def get_invoice(self, id):
    #     """
    #     Get invoice details for a POS order.
    #     id: POS order reference ID.
    #     return: Invoice details including ID, name, base URL, and QR code.
    #     """
    #     pos_id = self.search([('pos_reference', '=', id)])
    #     pos_id.action_pos_order_invoice()
    #     base_url = self.env['ir.config_parameter'].get_param('web.base.url')
    #     invoice_id = self.env['account.move'].search(
    #         [('ref', '=', pos_id.name)])
    #     return {
    #         'invoice_id': invoice_id.id,
    #         'invoice_name': invoice_id.name,
    #         'base_url': base_url,
    #         'qr_code': invoice_id.account_barcode,
    #     }
