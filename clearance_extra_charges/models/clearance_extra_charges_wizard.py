from odoo import models, fields, api
from odoo.exceptions import UserError

class ClearanceExtraChargesWizard(models.TransientModel):
    _name = 'clearance.extra.charges.wizard'
    _description = 'Wizard for Handling Extra Charges on Clearance'

    clearance_request_id = fields.Many2one('clearance.request', string="Clearance Request")
    product_ids = fields.Many2many('product.product', string="Products")

    def create_invoice_action(self, *args, **kwargs):
        self.ensure_one()
        company_name = self.clearance_request_id.company_id.name

        # Define default account IDs based on the company
        if company_name in ['Farha Logistic Dammam', 'فرحه لوجستك الدمام']:
            default_account_id = 1215
        elif company_name in ['Farha Logistics Jeddah', 'فرحه لوجستك جدة']:
            default_account_id = 2393
        else:
            raise UserError("No default account found for the company associated with this clearance request.")

        invoice_lines = []
        for product in self.product_ids:
            account_id = (product.property_account_income_id.id or
                          product.categ_id.property_account_income_categ_id.id or
                          default_account_id)

            if not account_id:
                raise UserError(f'No income account found for the product "{product.display_name}" and no default account is configured.')

            invoice_line_vals = {
                'product_id': product.id,
                'quantity': 1,  # Default to 1, adjust as needed
                'name': product.display_name,
                'account_id': account_id,
                'price_unit': product.lst_price,
            }
            invoice_lines.append((0, 0, invoice_line_vals))

        invoice_vals = {
            'partner_id': self.clearance_request_id.partner_id.id,
            'move_type': 'out_invoice',
            'invoice_line_ids': invoice_lines,
            'clearance_request_id': self.clearance_request_id.id,
        }
        invoice = self.env['account.move'].create(invoice_vals)
        clearance_request = self.env['clearance.request'].browse(self.clearance_request_id.id)
        if clearance_request.state == 'delivery':
            clearance_request.extra_charges_delivery_wizard_status = True
        if clearance_request.state == 'customs_statement':
            clearance_request.extra_charges_customs_statement_wizard_status = True
          
        return {
            'name': 'Invoice for Extra Charges',
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': invoice.id,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'current',
        }
