from odoo import _, models
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = "res.partner"

    def unlink(self):
        moves = (
            self.sudo()
            .env["account.move"]
            .search_count(
                [("partner_id", "in", self.ids), ("state", "in", ["draft", "posted"])]
            )
        )
        if moves:
            raise UserError(_("Record cannot be deleted. Partner used in Accounting"))
        return super(models.Model, self).unlink()
