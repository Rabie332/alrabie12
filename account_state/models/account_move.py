from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    ########################################################################
    # Fields
    ########################################################################
    state = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("under_review", "Under Review"),
            ("reviewed", "Reviewed"),
            ("confirm", "Confirm"),
            ("posted", "Validated"),
            ("cancel", "Cancelled"),
        ],
        default="draft",
        ondelete={"draft": "set default"},
    )

    ########################################################################
    # Compute methods
    ########################################################################
    @api.depends("restrict_mode_hash_table", "state")
    def _compute_show_reset_to_draft_button(self):
        for move in self:
            move.show_reset_to_draft_button = (
                not move.restrict_mode_hash_table
                and move.state
                in ("under_review", "reviewed", "confirm", "posted", "cancel")
            )

    ########################################################################
    # Methods
    ########################################################################
    def _make_done_activity(self, activity_types):
        """Make done activities."""
        for move in self:
            activities = self.env["mail.activity"].search(
                [
                    ("activity_type_id", "in", activity_types),
                    ("res_model", "=", move._name),
                    ("res_id", "=", move.id),
                ]
            )
            activities.unlink()

    def action_review(self):
        for move in self:
            move.state = "under_review"
            activity = "account_state.mail_assigned_invoice_to_review"
            users = (
                move.env.ref("account_state.group_account_reviewer")
                .sudo()
                .users.filtered(lambda user: user.id not in [1, 3])
            )
            if move.move_type == "entry":
                # only users who have at least group "Show Accounting Features - Readonly"
                # will receive this activity.
                users = (
                    move.env.ref("account.group_account_readonly")
                    .sudo()
                    .users.filtered(lambda user: user.id in users.ids)
                )
                activity = "account_state.mail_assigned_move_to_review"
            for user in users:
                move.sudo().activity_schedule(activity, user_id=user.id)

    def action_confirm(self):
        for move in self:
            move._make_done_activity(
                [
                    move.env.ref("account_state.mail_assigned_invoice_to_review").id,
                    move.env.ref("account_state.mail_assigned_move_to_review").id,
                    move.env.ref(
                        "account_state.mail_assigned_invoice_to_under_review"
                    ).id,
                    move.env.ref(
                        "account_state.mail_assigned_entry_to_under_review"
                    ).id,
                ]
            )
            move.state = "confirm"
            users = (
                self.env.ref("account.group_account_manager")
                .sudo()
                .users.filtered(lambda user: user.id not in [1, 3])
            )
            if move.move_type == "entry":
                # only users who have at least group "Show Accounting Features - Readonly"
                # will receive this activity.
                users = (
                    move.env.ref("account.group_account_readonly")
                    .sudo()
                    .users.filtered(lambda user: user.id in users.ids)
                )
                activity = "account_state.mail_assigned_entry_to_confirm"
            else:
                activity = "account_state.mail_assigned_invoice_to_confirm"
            for user in users:
                move.sudo().activity_schedule(activity, user_id=user.id)

    def action_reviewed(self):
        for move in self:
            move.state = "reviewed"
            # close activity
            self._make_done_activity(
                [
                    self.env.ref("account_state.mail_assigned_invoice_to_review").id,
                    self.env.ref("account_state.mail_assigned_move_to_review").id,
                ]
            )
            users = (
                self.env.ref("account_state.group_account_confirm_user")
                .sudo()
                .users.filtered(lambda user: user.id not in [1, 3])
            )
            # send activity to users who has confirm group
            activity = "account_state.mail_assigned_invoice_to_under_review"
            if move.move_type == "entry":
                activity = "account_state.mail_assigned_entry_to_under_review"
            for user in users:
                move.sudo().activity_schedule(activity, user_id=user.id)

    def action_post(self):
        super(AccountMove, self).action_post()
        self._make_done_activity(
            [
                self.env.ref("account_state.mail_assigned_entry_to_confirm").id,
                self.env.ref("account_state.mail_assigned_invoice_to_confirm").id,
            ]
        )

    def get_approvals_details(self, field="state", states=()):
        """Get approvers based on state."""
        for request in self:
            track_obj = request.env["mail.tracking.value"]
            ir_model = self.env["ir.model"].search([("model", "=", "account.move")])
            ir_model_field = request.env["ir.model.fields"].search(
                [("model_id", "=", ir_model.id), ("name", "=", field)]
            )
            # get tracking
            tracking_line = track_obj.sudo().search(
                [
                    ("mail_message_id.res_id", "=", request.id),
                    ("mail_message_id.model", "=", "account.move"),
                    ("field", "=", ir_model_field.id),
                    ("old_value_char", "in", states),
                ],
            )
            if tracking_line:
                # get date, approver, signature
                values = {
                    "date": tracking_line[-1].mail_message_id.date.date()
                    if tracking_line[-1].mail_message_id.date
                    else "",
                    "approver": tracking_line[-1].create_uid.name,
                    "signature": tracking_line[-1].create_uid.digital_signature,
                }
                return values


class ValidateAccountMove(models.TransientModel):
    _inherit = "validate.account.move"

    def validate_move(self):
        if self._context.get("active_model") == "account.move":
            domain = [("id", "in", self._context.get("active_ids", []))]
        elif self._context.get("active_model") == "account.journal":
            domain = [("journal_id", "=", self._context.get("active_id"))]
        else:
            raise UserError(_("Missing 'active_model' in context."))
        moves = self.env["account.move"].search(domain).filtered("line_ids")
        if not moves:
            raise UserError(_("There are no journal items in the draft state to post."))
        confirm_moves = moves.filtered(lambda move: move.state == "confirm")
        confirm_moves._post(not self.force_post)
        reviewed_moves = moves.filtered(lambda move: move.state == "reviewed")
        reviewed_moves.action_confirm()
        review_moves = moves.filtered(lambda move: move.state == "under_review")
        review_moves.action_reviewed()
        draft_moves = moves.filtered(lambda move: move.state == "draft")
        draft_moves.action_review()
        return {"type": "ir.actions.act_window_close"}
