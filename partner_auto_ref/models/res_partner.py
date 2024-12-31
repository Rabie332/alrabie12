from odoo import api, models


class ResPartner(models.Model):
    _inherit = "res.partner"
    _order = "name"

    def _get_excluded_partners(self):
        """Get excluded partner"""
        # get partners related to companies
        partner_companies = (
            self.sudo().env["res.company"].search([]).mapped("partner_id").ids
        )
        # get partners related to users
        partner_users = self.sudo().env["res.users"].search([]).mapped("partner_id").ids
        # get excluded partners : partners related to companies and users
        excluded_partners = partner_companies + partner_users
        return excluded_partners

    def _get_last_number_by_company(self):
        domain = [
            ("id", "!=", self._origin.id),
            ("ref", "!=", ""),
            ("id", "not in", self._get_excluded_partners()),
        ]
        if self.company_id:
            domain += [("company_id", "=", self.company_id.id)]
        else:
            domain += [("company_id", "=", False)]
        number = self.search(domain, order="ref desc", limit=1).ref
        return number

    # ------------------------------------------------------
    # ORM Method
    # ------------------------------------------------------
    @api.model
    def create(self, vals):
        """Add Partner number by company."""
        partner = super(ResPartner, self).create(vals)
        if (
            partner
            and not partner.ref
            and partner.id not in partner._get_excluded_partners()
        ):
            # get last ref of partners by company
            number = partner._get_last_number_by_company()
            if number:
                number = str(int(number) + 1).rjust(3, "0")
            else:
                number = "001"
            partner.ref = number
        return partner

    @api.onchange("company_id")
    def _onchange_company(self):
        self.ref = ""
        if self._origin.id not in self._get_excluded_partners():
            # get last ref of partners by company
            number = self._get_last_number_by_company()
            if number:
                number = str(int(number) + 1).rjust(3, "0")
            else:
                number = "001"
            self.ref = number
