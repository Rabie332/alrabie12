from odoo import _, api, fields, models


class ContractAllowanceLine(models.Model):
    _name = "hr.contract.allowance.line"
    _rec_name = "rule_id"
    _description = "Contract Allowance Line"

    rule_id = fields.Many2one(
        "hr.salary.rule",
        string="Salary rule",
        domain="['|', ('is_specific_allowance', '=', True), ('is_variable_bonus', '=', True)]",
    )
    is_variable_bonus = fields.Boolean(
        string="Variable Bonus", related="rule_id.is_variable_bonus"
    )
    contract_id = fields.Many2one("hr.contract", string="Contract")
    amount = fields.Float(string="Amount", digits="Payroll")

    _sql_constraints = [
        (
            "rule_uniq",
            "unique(rule_id, contract_id)",
            _("The rule already exists!"),
        )
    ]


class HrContract(models.Model):
    _inherit = "hr.contract"

    total_bonus = fields.Float(
        string="Sum Allowances and Fixed Bonus",
        digits="Payroll",
        compute="_compute_total_bonus",
        store=True,
    )
    allowances_ids = fields.One2many(
        "hr.contract.allowance.line", "contract_id", string="Allowances"
    )

    @api.depends("allowances_ids.is_variable_bonus", "allowances_ids.amount")
    def _compute_total_bonus(self):
        for record in self:
            record.total_bonus = sum(
                line.amount
                for line in record.allowances_ids.filtered(
                    lambda l: not l.is_variable_bonus
                )
            )

    def get_all_structures(self):
        """
        @return: the structures linked to the given contracts, ordered by
                 hierarchy (parent=False first, then first level children and
                 so on) and without duplicate
        """
        structures = self.mapped("struct_id")
        if not structures:
            return []
        # YTI TODO return browse records
        return list(set(structures._get_parent_structure().ids))
