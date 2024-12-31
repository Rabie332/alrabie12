from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_is_zero


class HrExpenseSheet(models.Model):
    _inherit = "hr.expense.sheet"

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submit", "Submitted"),
            ("to_review", "To Review"),
            ("reviewed", "Reviewed"),
            ("approve", "Confirm"),
            ("post", "Confirmed"),
            ("done", "Validated"),
            ("cancel", "Refused"),
        ]
    )
    move_line_ids = fields.One2many(
        "account.move.line",
        related="account_move_id.line_ids",
        string="Journal Lines",
        readonly=1,
    )
    _sql_constraints = [
        (
            "journal_id_required_posted",
            "CHECK(1=1)",
            "The journal must be set on posted expense",
        ),
    ]

    def _make_done_activity(self, activity_types):
        """Make done activities."""
        for expense in self:
            activitys = self.env["mail.activity"].search(
                [
                    ("activity_type_id", "in", activity_types),
                    ("res_model", "=", expense._name),
                    ("res_id", "=", expense.id),
                ]
            )
            activitys.write({"active": False})

    def activity_update(self):
        super(HrExpenseSheet, self).activity_update()
        self.filtered(lambda hol: hol.state == "cancel")._make_done_activity(
            [
                self.env.ref("hr_expense_states.mail_assigned_expense_to_review").id,
                self.env.ref("hr_expense_states.mail_assigned_expense_to_confirm").id,
                self.env.ref("hr_expense_states.mail_assigned_expense_to_validate").id,
            ]
        )

    def approve_expense_sheets(self):
        if not self.user_has_groups("hr_expense.group_hr_expense_team_approver"):
            raise UserError(_("Only Managers and HR Officers can approve expenses"))
        elif not self.user_has_groups("hr_expense.group_hr_expense_manager"):
            current_managers = (
                self.employee_id.expense_manager_id
                | self.employee_id.parent_id.user_id
                | self.employee_id.department_id.manager_id.user_id
            )

            if self.employee_id.user_id == self.env.user:
                raise UserError(_("You cannot approve your own expenses"))

            if (
                self.env.user not in current_managers
                and not self.user_has_groups("hr_expense.group_hr_expense_user")
                and self.employee_id.expense_manager_id != self.env.user
            ):
                raise UserError(_("You can only approve your department expenses"))

        responsible_id = self.user_id.id or self.env.user.id
        self.write({"state": "to_review", "user_id": responsible_id})
        self.activity_feedback(["hr_expense.mail_act_expense_approval"])
        activity = "hr_expense_states.mail_assigned_expense_to_review"
        users = (
            self.env.ref("account_state.group_account_reviewer")
            .sudo()
            .users.filtered(
                lambda user: self.company_id.id in user.company_ids.ids
                and user.id not in [1, 3]
            )
        )
        for user in users:
            self.sudo().activity_schedule(activity, user_id=user.id)

    def action_reviewed(self):
        for rec in self:
            rec.state = "reviewed"
            rec._make_done_activity(
                [
                    rec.env.ref("hr_expense_states.mail_assigned_expense_to_review").id,
                ]
            )
            activity = "hr_expense_states.mail_assigned_expense_to_confirm"
            users = (
                self.env.ref("account_state.group_account_confirm_user")
                .sudo()
                .users.filtered(
                    lambda user: self.company_id.id in user.company_ids.ids
                    and user.id not in [1, 3]
                )
            )
            for user in users:
                self.sudo().activity_schedule(activity, user_id=user.id)

    def action_confirm(self):
        for rec in self:
            rec.state = "approve"
            rec._make_done_activity(
                [
                    rec.env.ref(
                        "hr_expense_states.mail_assigned_expense_to_confirm"
                    ).id,
                ]
            )
            activity = "hr_expense_states.mail_assigned_expense_to_validate"
            users = (
                self.env.ref("account_state.group_account_confirm_user")
                .sudo()
                .users.filtered(
                    lambda user: self.company_id.id in user.company_ids.ids
                    and user.id not in [1, 3]
                )
            )
            for user in users:
                self.sudo().activity_schedule(activity, user_id=user.id)

    def action_sheet_move_create(self):
        samples = self.mapped("expense_line_ids.sample")
        if samples.count(True):
            if samples.count(False):
                raise UserError(_("You can't mix sample expenses and regular ones"))
            self.write({"state": "post"})
            return

        if any(sheet.state != "post" for sheet in self):
            raise UserError(
                _("You can only generate accounting entry for approved expense(s).")
            )
        if any(
            sheet.payment_mode == "own_account" and not sheet.journal_id
            for sheet in self
        ):
            raise UserError(
                _(
                    "Expenses must have an expense journal specified"
                    " to generate accounting entries."
                )
            )

        expense_line_ids = self.mapped("expense_line_ids").filtered(
            lambda r: not float_is_zero(
                r.total_amount,
                precision_rounding=(
                    r.currency_id or self.env.company.currency_id
                ).rounding,
            )
        )
        res = expense_line_ids.action_move_create()
        for sheet in self.filtered(lambda s: not s.accounting_date):
            sheet.accounting_date = sheet.account_move_id.date
        to_post = self.filtered(
            lambda sheet: sheet.payment_mode == "own_account" and sheet.expense_line_ids
        )
        to_post.write({"state": "post"})
        (self - to_post).write({"state": "done"})
        self.activity_update()
        return res

    def action_post(self):
        for rec in self:
            rec.state = "post"
            rec._make_done_activity(
                [
                    rec.env.ref(
                        "hr_expense_states.mail_assigned_expense_to_validate"
                    ).id,
                ]
            )

    def refuse_sheet(self, reason):
        for sheet in self:
            sheet.state = "cancel"
            sheet.message_post_with_view(
                "hr_expense.hr_expense_template_refuse_reason",
                values={"reason": reason, "is_sheet": True, "name": self.name},
            )
            sheet.activity_update()

    def reset_expense_sheets(self):
        if self.account_move_id:
            if self.payment_mode == "own_account" and self.state == "done":
                raise ValidationError(
                    _(
                        "The expense cannot be set as a draft because"
                        " it is paid by an employee."
                    )
                )
            self.account_move_id.button_cancel()
            self.account_move_id = False
        return super(HrExpenseSheet, self).reset_expense_sheets()


class HrExpense(models.Model):
    _inherit = "hr.expense"

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("reported", "Submitted"),
            ("to_review", "To Review"),
            ("reviewed", "Reviewed"),
            ("approve", "Confirm"),
            ("approved", "Confirmed"),
            ("done", "Validated"),
            ("refused", "Refused"),
        ]
    )

    @api.depends("sheet_id", "sheet_id.account_move_id", "sheet_id.state")
    def _compute_state(self):
        for expense in self:
            super(HrExpense, expense)._compute_state()
            if expense.sheet_id.state == "to_review":
                expense.state = "to_review"
            if expense.sheet_id.state == "reviewed":
                expense.state = "reviewed"
            if expense.sheet_id.state == "approve":
                expense.state = "approve"
