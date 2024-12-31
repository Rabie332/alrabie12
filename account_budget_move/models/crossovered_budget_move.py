from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class CrossoveredBudgetMove(models.Model):
    _name = "crossovered.budget.move"
    _description = "Crossovered Budget Move"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"

    name = fields.Char(string="Number", readonly=1)
    crossovered_budget_id = fields.Many2one(
        "crossovered.budget",
        string="Budget",
        required=1,
        domain=[("state", "=", "done")],
        readonly=1,
        states={"in_prepare": [("readonly", 0)]},
    )
    from_crossovered_budget_line_id = fields.Many2one(
        "crossovered.budget.lines",
        string="From Budgetary Position",
        required=1,
        readonly=1,
        states={"in_prepare": [("readonly", 0)]},
    )
    to_crossovered_budget_move_ids = fields.One2many(
        "crossovered.budget.move.lines",
        "crossovered_budget_move_id",
        string="To Budgetary Positions",
        required=1,
        readonly=1,
        states={"in_prepare": [("readonly", 0)]},
    )
    amount_move = fields.Float(
        string="Amount Move",
        required=1,
        readonly=1,
        states={"in_prepare": [("readonly", 0)]},
    )
    percent_move = fields.Float(string="Percent Move (%)", readonly=1)
    reason_move = fields.Text(
        string="Reason Move",
        required=1,
        readonly=1,
        states={"in_prepare": [("readonly", 0)]},
    )
    attachment_ids = fields.Many2many(
        "ir.attachment",
        string="Attachments",
        readonly=1,
        states={"in_prepare": [("readonly", 0)]},
    )
    date = fields.Date(string="Request Date", default=fields.Datetime.now, readonly=1)
    state = fields.Selection(
        [
            ("in_prepare", "In Prepare"),
            ("in_review", "In Review"),
            ("to_confirm", "To Confirm"),
            ("confirmed", "Confirmed"),
            ("validated", "Validated"),
            ("refused", "Refused"),
        ],
        string="State",
        default="in_prepare",
        tracking=True,
    )

    @api.model
    def create(self, vals):
        """Add sequence."""
        vals.update(
            {
                "name": self.env["ir.sequence"].next_by_code(
                    "crossovered.budget.move.seq"
                )
            }
        )
        return super(CrossoveredBudgetMove, self).create(vals)

    @api.onchange("amount_move", "from_crossovered_budget_line_id")
    def _onchange_amount_move(self):
        if (
            self.amount_move
            and self.from_crossovered_budget_line_id
            and self.from_crossovered_budget_line_id.planned_amount > 0
        ):
            self.percent_move = (
                self.amount_move / self.from_crossovered_budget_line_id.planned_amount
            ) * 100

    def action_move_amount(self):
        """Move amount from from_crossovered_budget_line_id
        to to_crossovered_budget_line_ids."""
        for record in self:
            for line in self.to_crossovered_budget_move_ids:
                line.to_crossovered_budget_line_id.planned_amount += line.amount_move
            record.from_crossovered_budget_line_id.planned_amount -= record.amount_move

    def action_to_review(self):
        for rec in self:
            if rec.state == "in_prepare":
                if not rec.to_crossovered_budget_move_ids:
                    raise ValidationError(_("You should choose at list one item"))
                exist_crossovered_budget_list = []
                total_amount_move = 0
                for line in rec.to_crossovered_budget_move_ids:
                    if (
                        line.to_crossovered_budget_line_id.id
                        in exist_crossovered_budget_list
                    ):
                        raise ValidationError(
                            _(
                                "Item %s already exists."
                                % line.to_crossovered_budget_line_id.general_budget_id.name
                            )
                        )
                    exist_crossovered_budget_list.append(
                        line.to_crossovered_budget_line_id.id
                    )
                    if (
                        line.to_crossovered_budget_line_id.id
                        == rec.from_crossovered_budget_line_id.id
                    ):
                        raise ValidationError(
                            _(
                                "You choose the some item, please choose different items."
                            )
                        )
                    total_amount_move += line.amount_move
                if rec.amount_move <= 0:
                    raise ValidationError(_("The amount move must be greater than 0."))
                if rec.amount_move > rec.from_crossovered_budget_line_id.planned_amount:
                    raise ValidationError(
                        _(
                            "The amount move must be less than amount of crossovered budget."
                        )
                    )
                if total_amount_move > rec.amount_move:
                    raise ValidationError(
                        _(
                            "The amount move must be less than "
                            "amount of crossovered budget line."
                        )
                    )
                if total_amount_move < rec.amount_move:
                    raise ValidationError(
                        _(
                            "The amount move must be equal "
                            "to the amount of crossovered budget line."
                        )
                    )
                rec.state = "in_review"
                for user in rec.env.ref("account_state.group_account_reviewer").users:
                    rec.activity_schedule(
                        "account_budget_move.mail_crossovered_budget_move_to_review",
                        user_id=user.id,
                    )

    def action_to_confirm(self):
        for rec in self:
            if rec.state == "in_review":
                rec.state = "to_confirm"
                for user in rec.env.ref(
                    "account_state.group_account_confirm_user"
                ).users:
                    rec.activity_schedule(
                        "account_budget_move.mail_crossovered_budget_move_to_confirm",
                        user_id=user.id,
                    )

    def action_confirm(self):
        for rec in self:
            if rec.state == "to_confirm":
                rec.state = "confirmed"
                for user in rec.env.ref("account.group_account_manager").users:
                    rec.activity_schedule(
                        "account_budget_move.mail_crossovered_budget_move_confirm",
                        user_id=user.id,
                    )

    def action_validate(self):
        for rec in self:
            if rec.state == "confirmed":
                rec.action_move_amount()
                rec.state = "validated"

    def action_refuse(self):
        for rec in self:
            rec.state = "refused"


class CrossoveredBudgetMoveLines(models.Model):
    _name = "crossovered.budget.move.lines"
    _description = "Crossovered Budget Move Lines"

    to_crossovered_budget_line_id = fields.Many2one(
        "crossovered.budget.lines", string="To Budgetary Position", required=1
    )
    crossovered_budget_move_id = fields.Many2one(
        "crossovered.budget.move", string="Budgetary Position"
    )
    amount_move = fields.Float(string="Amount Move", required=1)
    percent_move = fields.Float(string="Percent Move (%)", readonly=1)

    @api.constrains("amount_move")
    def _check_amount(self):
        for rec in self:
            if rec.amount_move <= 0:
                raise ValidationError(_("The amount move must be greater than 0."))

    @api.onchange("amount_move", "to_crossovered_budget_line_id")
    def _onchange_amount_move(self):
        if self.amount_move:
            if self.amount_move > self.to_crossovered_budget_line_id.planned_amount:
                self.percent_move = 100
            else:
                if (
                    self.to_crossovered_budget_line_id
                    and self.to_crossovered_budget_line_id.planned_amount > 0
                ):
                    self.percent_move = (
                        self.amount_move
                        / self.to_crossovered_budget_line_id.planned_amount
                    ) * 100
