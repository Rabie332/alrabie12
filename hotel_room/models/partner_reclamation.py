from odoo import api, fields, models


class PartnerReclamation(models.Model):
    _name = "partner.reclamation"
    _description = "Partner Reclamation"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char("Name", readonly=True)
    date = fields.Datetime(
        "Date",
        readonly=True,
        required=True,
        states={"draft": [("readonly", False)]},
        default=lambda self: fields.Datetime.now(),
    )

    partner_id = fields.Many2one(
        "res.partner",
        "Guest",
        readonly=True,
        index=True,
        required=True,
        domain="[('is_guest', '=', True)]",
        states={"draft": [("readonly", False)]},
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("progress", "In progress"),
            ("solved", "Solved"),
            ("cancel", "Cancelled"),
        ],
        "State",
        readonly=True,
        default="draft",
        tracking=1,
    )
    complaint_text = fields.Text(
        string="Complaint text",
        readonly=True,
        required=True,
        states={"draft": [("readonly", False)]},
    )

    company_id = fields.Many2one(
        "res.company",
        "Hotel",
        readonly=True,
        required=True,
        default=lambda self: self.env.company,
        states={"draft": [("readonly", False)]},
    )
    active = fields.Boolean(string="Active", default=True)

    @api.model
    def create(self, vals):
        """Add sequence."""
        reclamation = super(PartnerReclamation, self).create(vals)
        if reclamation:
            reclamation.name = self.env["ir.sequence"].next_by_code(
                "partner.reclamation.seq"
            )
        return reclamation

    def action_progress(self):
        self.state = "progress"

    def action_solved(self):
        self.state = "solved"

    def action_cancel(self):
        self.state = "cancel"
