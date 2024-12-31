from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    payments_rewards_amount = fields.Float(
        string="Payments Rewards Amount", compute="_compute_payments_rewards", tracking=True
    )
    employee_cars_count = fields.Integer(
        groups="base.group_user", tracking=True)

    # ------------------------------------------------------
    # Business Methods
    # ------------------------------------------------------

    def transportation_rewards_payments(self):
        """Get reward for drivers."""
        action = self.env.ref(
            "account.action_account_payments").sudo().read()[0]
        for employee in self:
            action["domain"] = [
                ("partner_id", "=", employee.address_home_id.id),
                ("is_reward_drivers", "=", True),
            ]
            action["context"] = {
                "default_is_reward_drivers": True,
            }
            action["views"] = [
                (
                    self.env.ref(
                        "transportation.view_account_payment_tree_reward_transportation"
                    ).id,
                    "tree",
                )
            ]
        return action

    # ------------------------------------------------------------
    # Compute methods
    # ------------------------------------------------------------

    def _compute_payments_rewards(self):
        """Calculate payments drivers."""
        for request in self:
            payments = self.env["account.payment"].search(
                [
                    ("partner_id", "=", request.address_home_id.id),
                    ("is_reward_drivers", "=", True),
                    ("state", "!=", "cancel"),
                ]
            )
            request.payments_rewards_amount = sum(payments.mapped("amount"))
