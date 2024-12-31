from odoo import fields, models, api, _
from odoo.exceptions import UserError


EXEMPTION_REASON_CODES = [
    ('VATEX-SA-29', 'VATEX-SA-29 Financial services mentioned in Article 29 of the VAT Regulations.'),
    ('VATEX-SA-29-7', 'VATEX-SA-29-7 Life insurance services mentioned in Article 29 of the VAT.'),
    ('VATEX-SA-30', 'VATEX-SA-30 Real estate transactions mentioned in Article 30 of the VAT Regulations.'),
    ('VATEX-SA-32', 'VATEX-SA-32 Export of goods.'),
    ('VATEX-SA-33', 'VATEX-SA-33 Export of Services.'),
    ('VATEX-SA-34-1', 'VATEX-SA-34-1 The international transport of Goods.'),
    ('VATEX-SA-34-2', 'VATEX-SA-34-1 The international transport of Passengers.'),
    ('VATEX-SA-34-3', 'VATEX-SA-34-3 Services directly connected and incidental to a Supply of international passenger transport.'),
    ('VATEX-SA-34-4', 'VATEX-SA-34-4 Supply of a qualifying means of transport.'),
    ('VATEX-SA-34-5', 'VATEX-SA-34-5 Any services relating to Goods or passenger transportation, as defined in article twenty five of these Regulations.'),
    ('VATEX-SA-35', 'VATEX-SA-35 Medicines and medical equipment.'),
    ('VATEX-SA-36', 'VATEX-SA-36 Qualifying metals.'),
    ('VATEX-SA-EDU', 'VATEX-SA-EDU Private education to citizen.'),
    ('VATEX-SA-HEA', 'VATEX-SA-HEA Private healthcare to citizen.'),
    ('VATEX-SA-MLTRY', 'VATEX-SA-MLTRY Supply of qualified military goods.'),
    ('VATEX-SA-OOS', 'VATEX-SA-OOS Reason is free text.')
]


class AccountTax(models.Model):
    _inherit = 'account.tax'

    exemption_reason_code = fields.Selection(string="Exemption Reason Code",
                                                     selection=EXEMPTION_REASON_CODES, help="Tax Exemption Reason Code (ZATCA)")
    free_exemption_reason = fields.Char(string="Exemption Reason")


class AccountTaxTemplate(models.Model):
    _inherit = 'account.tax.template'

    exemption_reason_code = fields.Selection(string="Exemption Reason Code",
                                                     selection=EXEMPTION_REASON_CODES, help="Tax Exemption Reason Code (ZATCA)")
    free_exemption_reason = fields.Char(string="Exemption Reason")

    def _get_tax_vals(self, company, tax_template_to_tax):
        # OVERRIDE
        res = super()._get_tax_vals(company, tax_template_to_tax)
        res['exemption_reason_code'] = self.exemption_reason_code
        res['free_exemption_reason'] = self.free_exemption_reason
        return res
