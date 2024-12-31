from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HrInfraction(models.Model):
    _name = "hr.infraction"
    _inherit = ["request"]
    _description = "Infraction"

    description = fields.Text(
        string="Description", readonly=1, states={"draft": [("readonly", 0)]}
    )
    active = fields.Boolean("Active", default=True)
    request_type_id = fields.Many2one(required=True)

    number_days = fields.Float(string="Number of days", readonly=True)
    date_from = fields.Date(
        string="From", readonly=True, states={"draft": [("readonly", False)]}
    )
    date_to = fields.Date(
        string="To", readonly=True, states={"draft": [("readonly", False)]}
    )
    period_id = fields.Many2one(
        "hr.period",
        string="Period applied",
        required=True,
        readonly=1,
        states={"draft": [("readonly", 0)]},
    )
    type_deduction = fields.Selection(
        string="Deduction Type", related="request_type_id.infraction_type"
    )
    amount = fields.Float(
        string="Amount", readonly=1, states={"draft": [("readonly", 0)]}
    )

    # ------------------------------------------------------------
    # Onchange methods
    # ------------------------------------------------------------
    @api.onchange("date_from", "date_to")
    def _onchange_date(self):
        """Onchange date."""
        if self.date_from and self.date_to:
            if self.date_from > self.date_to:
                raise ValidationError(
                    _("The start date must be anterior to the end date.")
                )
            self.number_days = (self.date_to - self.date_from).days + 1

    # ------------------------------------------------------------
    # ORM methods
    # ------------------------------------------------------------
    @api.model
    def create(self, vals):
        """Add sequence."""
        infraction = super(HrInfraction, self).create(vals)
        if infraction:
            infraction.name = self.env["ir.sequence"].next_by_code("hr.infraction.seq")
        return infraction

    # ------------------------------------------------------------
    # Compute methods
    # ------------------------------------------------------------

    @api.depends("stage_id")
    def _compute_display_button(self):
        for infraction in self:
            super(HrInfraction, infraction)._compute_display_button()
            if infraction.state == "draft" and (
                (
                    infraction.create_uid
                    and infraction.create_uid.id == infraction.env.uid
                )
                or infraction.env.user.has_group(
                    "hr_infraction.hr_infraction_group_manager"
                )
            ):
                infraction.display_button_send = True

    # ------------------------------------------------------------
    # Constraints methods
    # ------------------------------------------------------------

    @api.constrains("amount")
    def _check_amount(self):
        if (
            self.request_type_id
            and self.request_type_id.infraction_type == "amount"
            and self.amount <= 0
        ):
            raise ValidationError(_("Amount should be greater than zero"))

    def print_report(self):
        return self.env.ref("hr_infraction.report_hr_infraction").report_action(self)


class HrInfractionType(models.Model):
    _inherit = ["request.type"]

    infraction_type = fields.Selection(
        [
            ("no_deduction", "Without Deduction"),
            ("amount", "Amount"),
            ("nb_days", "Number of Days"),
        ],
        string="Infraction Type",
    )

    @api.model
    def create(self, vals):
        """Create code."""
        if vals["res_model"] == "hr.infraction":
            code = self.env["ir.sequence"].next_by_code("request.type.seq")
            vals.update({"code": code})
        res = super(HrInfractionType, self).create(vals)
        return res
