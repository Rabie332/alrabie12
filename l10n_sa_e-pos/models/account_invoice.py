# -*- coding: utf-8 -*-

from odoo import fields, api, models, _
import base64
import qrcode
import io


class AccountMove(models.Model):
    _inherit = "account.move"

    l10n_sa_qr_code = fields.Binary(
        string="QRCode", compute="_compute_qr_code", readonly=True
    )

    @api.depends('l10n_sa_qr_code_str')
    def _compute_qr_code(self):
        for rec in self:
            rec.l10n_sa_qr_code = False
            qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=3,
                    border=4,
                )

            qr.add_data(rec.l10n_sa_qr_code_str)
            qr.make(fit=True)
            img = qr.make_image()
            temp = io.BytesIO()
            img.save(temp, format="PNG")
            qr_code_image = base64.b64encode(temp.getvalue())
            rec.l10n_sa_qr_code = qr_code_image
