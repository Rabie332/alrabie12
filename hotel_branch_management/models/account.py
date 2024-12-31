from odoo import api, fields, models


class AccountPayments(models.Model):
    _inherit = "account.payment"

    payment_branch_id = fields.Many2one(
        "hotel.branch", string="Payment Branch", )
    # related="reservation_id.reservation_branch_id"


class AccountMove(models.Model):
    _inherit = "account.move"

    reservation_id = fields.Many2one("hotel.reservation", "Reservation")
    invoice_branch_id = fields.Many2one(
        "hotel.branch", string="Invoice Branch", )
    # related="reservation_id.reservation_branch_id"


class AccountAccount(models.Model):
    _inherit = "account.account"

    account_branch_id = fields.Many2one(
        "hotel.branch", string="Account Branch")


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    account_line_branch_id = fields.Many2one(
        "hotel.branch", string="Account Branch")
    # , related="account_id.account_branch_id"
