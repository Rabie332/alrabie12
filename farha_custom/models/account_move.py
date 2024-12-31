from odoo import _, fields, models
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    active = fields.Boolean(string="Active", default=True)

    # ------------------------------------------------------
    # Business Methods
    # ------------------------------------------------------

    def toggle_active(self):
        for move in self:
            if move.state != "cancel":
                raise ValidationError(_("Only canceled entries can be archived"))
            move.with_context(active_test=False).line_ids.filtered(
                lambda line: line.active == move.active
            ).toggle_active()
            move.with_context(active_test=False).invoice_line_ids.filtered(
                lambda line: line.active == move.active
            ).toggle_active()
        super(AccountMove, self).toggle_active()

    def _get_integrity_hash_fields_and_subfields(self):
        """Resolve problem of archive of account move line."""
        return (
            super(AccountMove, self)._get_integrity_hash_fields_and_subfields()
            if self and self.line_ids
            else self._get_integrity_hash_fields()
        )


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    active = fields.Boolean(string="Active", default=True)
