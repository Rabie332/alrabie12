from odoo import api, fields, models


class QRCodeInvoice(models.Model):
    _inherit = "account.move"

    qr_code = fields.Char("QR Code", compute="_compute_qr_code", store=True)
    deliveryman_id = fields.Many2one(
        "res.users", string="Livreur", domain=[("code_carrier", "!=", False)]
    )

    @api.depends("name", "state")
    def _compute_qr_code(self):
        for move in self:
            qr_code = ""
            if move.move_type == "out_invoice" and move.state == "posted":
                base_url = (
                    self.env["ir.config_parameter"].sudo().get_param("web.base.url")
                )
                qr_code = "{}/check_carrier_code?number={}".format(base_url, move.name)
            move.qr_code = qr_code
