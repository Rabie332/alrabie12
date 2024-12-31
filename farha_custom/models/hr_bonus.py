from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HrBonus(models.Model):
    _inherit = "hr.bonus"

    hr_period_to_id = fields.Many2one(
        "hr.period",
        string="Period To",
        required=1,
        readonly=1,
        states={"draft": [("readonly", 0)]},
    )

    # ------------------------------------------------------------
    # Constraint methods
    # ------------------------------------------------------------
    @api.constrains("hr_period_id", "hr_period_to_id")
    def _check_periods(self):
        """Check periods FROM & TO."""
        for bonus in self:
            if (
                bonus.hr_period_id
                and bonus.hr_period_to_id
                and bonus.hr_period_id.date_end > bonus.hr_period_to_id.date_end
            ):
                raise ValidationError(_("Period To must be great than the period from"))


class HrBonusLine(models.Model):
    _inherit = "hr.bonus.line"

    @api.constrains("net_amount")
    def _check_net_amount(self):
        return True
