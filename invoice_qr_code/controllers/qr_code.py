from odoo import http
from odoo.http import request


class QrCodeController(http.Controller):
    @http.route(["/check_carrier_code"], type="http", auth="public")
    def check_carrier_code(self, number, **kw):
        """render authentication form"""
        values = {"number": number}
        return request.render("invoice_qr_code.invoice_qr_code_template", values)

    @http.route("/qr_code_action", type="http", auth="public", csrf=False)
    def qr_code_action(self, **kw):
        """Check invoice number and code_carrier :
        - if valid : execute methode execute_qr_code_action
        - else : render authentication form  with message error
        """
        invoice_number = kw.get("number")
        code_carrier = kw.get("code_carrier")
        message = ""
        order = (
            request.env["account.move"].sudo().search([("name", "=", invoice_number)])
        )
        if not order:
            message = "Numéro de la facture est incorrecte"
        user = (
            request.env["res.users"]
            .sudo()
            .search([("code_carrier", "=", code_carrier)])
        )
        if not user:
            message = "Code d'authentification est incorrecte"
        if message == "":
            self.execute_qr_code_action(invoice_number, code_carrier)
            return request.render("invoice_qr_code.invoice_qr_code_success_template")
        else:
            kw["error"] = message
        return request.render("invoice_qr_code.invoice_qr_code_template", kw)

    def execute_qr_code_action(self, invoice_number, code_carrier):
        # Redefine this methode to add logic for each client in scan of Qrcode.
        return True
