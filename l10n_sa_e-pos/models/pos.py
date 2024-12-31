# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _

import psycopg2
import logging

_logger = logging.getLogger(__name__)


class PosConfigInherit(models.Model):
    _inherit = "pos.config"

    default_partner_id = fields.Many2one(
        "res.partner", string="Default Customer", compute="_compute_default_partner_id"
    )

    def _compute_default_partner_id(self):
        partner_id = self.env.ref("l10n_sa_e-pos.partner_generic")
        for rec in self:
            rec.default_partner_id = partner_id and partner_id.id


class POSOrder(models.Model):
    _inherit = "pos.order"

    l10n_sa_send_state = fields.Selection(
        related="account_move.l10n_sa_send_state", string="E-Invoice Status")

    def get_qr_code(self):
        self.ensure_one()
        return self.account_move.l10n_sa_qr_code

    # def _prepare_invoice_vals(self):
    #     vals = super()._prepare_invoice_vals()
    #     if not vals["journal_id"]:
    #         journal_id = self.env["account.journal"].search(
    #             [("type", "=", "sale"), ("company_id", "=", self.env.company.id)], limit=1
    #         )
    #         vals["journal_id"] = journal_id.id
    #     return vals

    # @api.model
    # def _process_order(self, order, draft, existing_order):
    #     res = super(POSOrder, self)._process_order(order, draft, existing_order)
    #     pos_order = self.browse(res)
    #     if not pos_order.account_move and pos_order.company_id.country_id.code == "SA" and pos_order.state == "paid":
    #         pos_order._generate_pos_order_invoice()
    #     if pos_order.account_move:
    #         zatca_auto_send = self.env["ir.config_parameter"].sudo().get_param("l10n_sa_e-invoice.zatca_auto_send")
    #         if not zatca_auto_send:
    #             pos_order.account_move.attach_generated_xml()
    #     return pos_order.id

    # def action_send_pos_einvoices(self):
    #     """Send e-invoice related pos"""
    #     for order in self:
    #         if order.account_move:
    #             order.account_move.action_send_einvoices()
