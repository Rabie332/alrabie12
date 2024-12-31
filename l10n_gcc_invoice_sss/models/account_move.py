# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    l10n_gcc_invoice_tax_amount = fields.Float(
        compute='_compute_l10n_gcc_invoice_tax_amount',
        store=True,
        readonly=False
    )

    @api.depends('tax_ids', 'price_subtotal')
    def _compute_l10n_gcc_invoice_tax_amount(self):
        for line in self:
            # Ensure that a default value (e.g., 0.0) is always assigned to avoid CacheMiss errors.
            line.l10n_gcc_invoice_tax_amount = sum(
                tax.amount for tax in line.tax_ids
            ) if line.tax_ids else 0.0
