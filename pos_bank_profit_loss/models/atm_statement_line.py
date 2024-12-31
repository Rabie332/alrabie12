from odoo import fields, models


class AtmStatementLine(models.Model):
    _name = "atm.statement.line"
    _description = "ATM statement line"

    def _domain_payment_method(self):
        session_id = self.env.context.get("default_session_id")
        if session_id:
            session = self.env["pos.session"].browse(session_id)
            bank_payment_methods = session.payment_method_ids.filtered(
                lambda m: m.bank_statement
            )
            return [("id", "in", bank_payment_methods.ids)]

    payment_method_id = fields.Many2one(
        comodel_name="pos.payment.method",
        required=True,
        domain=_domain_payment_method,
    )
    amount = fields.Float(string="Amount", required=True)
    session_id = fields.Many2one("pos.session", string="Related session")
