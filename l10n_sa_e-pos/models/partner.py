# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = "res.partner"

    # def write(self, vals):
    #     partner_generic = self.env.ref('l10n_sa_e-pos.partner_generic')
    #     if partner_generic.id in self.ids:
    #         raise UserError(_("You cannot change Generic partner data"))
    #     return super(ResPartner, self).write(vals)

    def unlink(self):
        partner_generic = self.env.ref("l10n_sa_e-pos.partner_generic")
        if partner_generic.id in self.ids:
            raise UserError(_("You cannot delete Generic partner"))
        return super(ResPartner, self).unlink()
