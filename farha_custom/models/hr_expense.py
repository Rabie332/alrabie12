from odoo import api, fields, models


class HrExpenseSheet(models.Model):
    _inherit = "hr.expense.sheet"

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submit", "Direct manager"),
            ("to_review", "Financial Manger"),
            ("post", "Confirmed"),
            ("done", "Validated"),
            ("cancel", "Refused"),
        ]
    )

    def approve_expense_sheets(self):
        super(HrExpenseSheet, self).approve_expense_sheets()
        activity = "hr_expense_states.mail_assigned_expense_to_validate"
        reviewer_users = (
            self.env.ref("account_state.group_account_reviewer").sudo().users
        )
        users = (
            self.env.ref("account.group_account_manager").sudo().users
            + self.env.ref("account.group_account_invoice").sudo().users
            + self.env.ref("account_state.group_account_confirm_user").sudo().users
        )
        users = users.filtered(
            lambda user: self.company_id.id in user.company_ids.ids
            and user.id not in [1, 3]
            and user.id not in reviewer_users.ids
        )
        for user in set(users):
            self.sudo().activity_schedule(activity, user_id=user.id)


class HrExpense(models.Model):
    _inherit = "hr.expense"

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("reported", "Direct manager"),
            ("to_review", "Financial Manger"),
            ("post", "Confirmed"),
            ("done", "Validated"),
            ("refused", "Refused"),
        ]
    )

    @api.depends("sheet_id", "sheet_id.account_move_id", "sheet_id.state")
    def _compute_state(self):
        for expense in self:
            if not expense.sheet_id or expense.sheet_id.state == "draft":
                expense.state = "draft"
            elif expense.sheet_id.state == "submit":
                expense.state = "reported"
            elif expense.sheet_id.state == "cancel":
                expense.state = "refused"
            elif expense.sheet_id.state == "to_review":
                expense.state = "to_review"
            elif expense.sheet_id.state == "done":
                expense.state = "done"
            else:
                expense.state = "post"
