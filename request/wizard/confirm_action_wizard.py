from odoo import _, models
from odoo.exceptions import UserError


class ConfirmActionWizard(models.TransientModel):
    _name = "confirm.action.wizard"
    _description = "Confirm Action"

    def action_multi_refuse(self):
        requests = self.env[self._context.get("active_model")].browse(
            self._context.get("active_ids", [])
        )
        for request in requests:
            if not request.display_button_refuse:
                raise UserError(
                    _("You cannot refuse the request {}.").format(request.name)
                )
            request.action_refuse()

    def action_multi_accept(self):
        requests = self.env[self._context.get("active_model")].browse(
            self._context.get("active_ids", [])
        )
        for request in requests:
            if not request.display_button_accept:
                raise UserError(
                    _("You cannot accept the request {}.").format(request.name)
                )
            request.action_accept()
