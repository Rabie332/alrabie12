from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class HrBonus(models.Model):
    _name = "hr.bonus"
    _inherit = ["mail.thread"]
    _order = "id desc"
    _rec_name = "type_id"
    _description = "Bonus Request"

    def _default_hr_period_id(self):
        period_id = self.env["hr.period"].search(
            [
                ("state", "=", "open"),
                "|",
                ("company_id", "=", self.env.company.id),
                ("company_id", "=", False),
            ],
            limit=1,
        )
        return period_id

    date = fields.Date(
        string="Date",
        required=1,
        readonly=1,
        states={"draft": [("readonly", 0)]},
        default=fields.Date.context_today,
    )
    bonus_method = fields.Selection(
        string="Bonus by",
        selection=[("amount", "Amount"), ("percentage", "Percentage")],
        required=1,
        readonly=1,
        states={"draft": [("readonly", 0)]},
    )
    amount = fields.Float(
        string="Amount NET",
        digits="Payroll",
        readonly=1,
        states={"draft": [("readonly", 0)]},
    )
    total_amount = fields.Float(
        string="Total Amount GROSS",
        compute="_compute_total_amount",
        store=True,
        digits="Payroll",
    )
    type_id = fields.Many2one(
        "hr.salary.rule",
        string=" Bonus ",
        required=1,
        readonly=1,
        states={"draft": [("readonly", 0)]},
    )
    state = fields.Selection(
        [("draft", "Draft"), ("confirm", "Confirmed"), ("payed", "Payed")],
        string="State",
        default="draft",
        readonly=1,
        tracking=True,
    )
    target = fields.Selection(
        string="Target Group",
        selection=[
            ("employee", "Employees"),
            ("department", "Department"),
            ("tags", "Tags"),
        ],
        required=1,
        readonly=1,
        states={"draft": [("readonly", 0)]},
    )
    department_ids = fields.Many2many(
        "hr.department",
        string="Departments",
        readonly=1,
        states={"draft": [("readonly", 0)]},
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
    )
    employee_ids = fields.Many2many(
        "hr.employee",
        string="Employees",
        readonly=1,
        states={"draft": [("readonly", 0)]},
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        readonly=True,
        required=True,
        copy=False,
        default=lambda self: self.env.company,
        states={"draft": [("readonly", False)]},
    )
    hr_period_id = fields.Many2one(
        "hr.period",
        string="Period applied",
        required=1,
        readonly=1,
        states={"draft": [("readonly", 0)]},
        default=_default_hr_period_id,
    )
    line_ids = fields.One2many(
        "hr.bonus.line",
        "bonus_id",
        string="Details per employee",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    category_ids = fields.Many2many("hr.employee.category", string="Tags")
    is_variable_bonus = fields.Boolean(
        string="Is variable bonus", store=True, related="type_id.is_variable_bonus"
    )
    payslip_input_ids = fields.One2many("hr.payslip.input", "bonus_id", string="Inputs")
    display_button_set_to_draft = fields.Boolean(
        compute="_compute_display_button_set_draft"
    )

    @api.depends("payslip_input_ids", "state")
    def _compute_display_button_set_draft(self):
        for record in self:
            record.display_button_set_to_draft = False
            if record.state != "draft" and not record.payslip_input_ids:
                record.display_button_set_to_draft = True

    @api.depends("amount", "line_ids.amount", "bonus_method")
    def _compute_total_amount(self):
        """Compute the total amount."""
        for rec in self:
            if rec.bonus_method == "percentage":
                for emp in rec.employee_ids:
                    if emp.contract_id:
                        rec.total_amount += emp.contract_id.wage * (rec.amount / 100)
            else:
                rec.total_amount = sum(line.amount for line in rec.line_ids)

    @api.onchange("bonus_method")
    def onchange_bonus_method(self):
        if self.env.context.get("onchange_bonus_method"):
            self.department_ids = False
            self.category_ids = False
            self.employee_ids = False
            self.line_ids = [(5, False, False)]

    @api.onchange("target")
    def onchange_target(self):
        """Change Target."""
        if self.target == "employee":
            self.department_ids = False
            self.category_ids = False
            if self.env.context.get("onchange_target"):
                self.employee_ids = False
                self.line_ids = [(5, False, False)]

    @api.onchange("department_ids")
    def onchange_department_ids(self):
        if self.department_ids:
            self.line_ids = [(5, False, False)]
            self.employee_ids = False
            self.employee_ids = self.env["hr.employee"].search(
                [("department_id", "in", self.department_ids.ids)]
            )

    @api.onchange("category_ids")
    def onchange_category_ids(self):
        if self.category_ids:
            self.line_ids = [(5, False, False)]
            self.employee_ids = False
            self.employee_ids = self.env["hr.employee"].search(
                [("category_ids", "in", self.category_ids.ids)]
            )

    @api.onchange("amount")
    def onchange_amount(self):
        self.line_ids.write({"net_amount": self.amount, "amount": self.amount})

    @api.onchange("type_id")
    def onchange_type_id(self):
        self.line_ids = [(5, False, False)]
        self.employee_ids = False
        self.department_ids = False
        self.category_ids = False
        if self.type_id.is_variable_bonus:
            self.bonus_method = "amount"
            self.target = "employee"
            allowances = self.env["hr.contract.allowance.line"].search(
                [("contract_id.state", "=", "open"), ("rule_id", "=", self.type_id.id)]
            )
            for allowance in allowances:
                employee = allowance.contract_id.employee_id
                if employee.id not in self.employee_ids.ids:
                    self.employee_ids = [(4, employee.id)]
                self.env["hr.bonus.line"].new(
                    {
                        "employee_id": employee.id,
                        "base_amount": allowance.amount,
                        "percent": 0,
                        "net_amount": allowance.amount,
                        "amount": allowance.amount,
                        "bonus_id": self.id,
                    }
                )

    @api.onchange("employee_ids")
    def onchange_employee_ids(self):
        if self.env.context.get("onchange_employee"):
            self.line_ids = [(5, False, False)]
            if self.bonus_method == "amount":
                for employee in self.employee_ids:
                    base_amount = 0
                    if self.type_id.is_variable_bonus:
                        allowance = self.env["hr.contract.allowance.line"].search(
                            [
                                ("contract_id", "=", employee.contract_id.id),
                                ("contract_id.state", "=", "open"),
                                ("rule_id", "=", self.type_id.id),
                            ]
                        )
                        base_amount = allowance.amount
                    self.env["hr.bonus.line"].new(
                        {
                            "employee_id": employee._origin.id,
                            "base_amount": base_amount,
                            "percent": 0,
                            "net_amount": self.amount,
                            "amount": self.amount,
                            "bonus_id": self.id,
                        }
                    )

    def compute_bonus_gross(self, employee, amount):
        contract = employee.sudo().contract_ids.filtered(
            lambda contract: contract.state == "open"
        )

        if self.type_id.is_specific_bonus:
            net_paid = amount
        else:
            net_paid = contract[0].wage_net + amount

        # create payslip with current period
        value = {
            "name": "Nombre des jours travaillés 100%",
            "sequence": 1,
            "code": "WORK100",
            "number_of_days": self.hr_period_id.number_worked_days,
            "contract_id": contract.id,
        }

        # this field work_entry_type_id used in odoo enterprise to create payslip lines
        # this condition to update this method to odoo oca and odoo enterprise
        if "work_entry_type_id" in self.env["hr.payslip.worked_days"]._fields:
            value.update(
                {
                    "work_entry_type_id": self.env["hr.work.entry.type"]
                    .search([("code", "=", "WORK100")])
                    .id
                }
            )

        # for odoo oca get structure from contract but for odoo enterprise
        # get it from structure type
        if "default_struct_id" in self.env["hr.payroll.structure.type"]._fields:
            if contract.structure_type_id.default_struct_id:
                structure = contract.structure_type_id.default_struct_id
            else:
                raise ValidationError(
                    _("Please add a regular pay structure for salary structure type.")
                )
        else:
            structure = contract.sudo().struct_id

        payslip = (
            self.env["hr.payslip"]
            .sudo()
            .create(
                {
                    "name": "Payslip",
                    "employee_id": employee.id,
                    "contract_id": contract.id,
                    "struct_id": structure.id,
                    "hr_period_id": self.hr_period_id.id,
                    "is_specific_struct": self.type_id.is_specific_bonus,
                    "worked_days_line_ids": [(0, 0, value)],
                    "input_line_ids": [
                        (
                            0,
                            0,
                            {
                                "name": self.sudo().type_id.name,
                                "code": self.sudo().type_id.code,
                                "amount": amount,
                                "contract_id": contract.id,
                            },
                        )
                    ],
                }
            )
        )

        amount_net = 0
        while net_paid - amount_net > 0:
            payslip.compute_sheet()
            payslip_line_net = payslip.line_ids.filtered(
                lambda line: line.code.startswith("NET_PAYER")
            )
            payslip_line_bonus = payslip.line_ids.filtered(
                lambda line: line.code == self.type_id.code
            )
            amount_bonus = payslip_line_bonus[0].total
            if payslip_line_net:
                amount_net = payslip_line_net[0].total
            else:
                amount_net = payslip.line_ids.filtered(lambda line: line.code == "NET")[
                    0
                ].total
            # increase amount bonus until net paid is equal to amount net
            if net_paid > amount_net:
                diff = net_paid - amount_net
                if diff > 100:
                    amount_bonus += 100
                elif diff > 50:
                    amount_bonus += 50
                elif diff > 10:
                    amount_bonus += 10
                elif diff > 5:
                    amount_bonus += 5
                elif diff > 1:
                    amount_bonus += 1
                elif diff > 0.5:
                    amount_bonus += 0.5
                elif diff > 0.1:
                    amount_bonus += 0.1
                elif diff > 0.01:
                    amount_bonus += 0.01
                else:
                    amount_bonus += 0.001
            payslip.sudo().input_line_ids.filtered(
                lambda line: line.code == self.type_id.code
            )[0].amount = amount_bonus
        # delete payslip created
        payslip.action_payslip_cancel()
        payslip.unlink()
        return amount_bonus

    def compute_gross_per_employee(self):
        if not self.line_ids:
            raise ValidationError(_("You must select an employee."))
        if not self.hr_period_id.number_worked_days:
            raise ValidationError(
                _("Please add number work days to the current period.")
            )
        # check if any employee hasn't contract
        lines = self.line_ids.filtered(
            lambda l: not l.employee_id.contract_id
            or l.employee_id.contract_id.state != "open"
        )
        if lines:
            raise ValidationError(_("%s hasn't a contract" % lines[0].employee_id.name))

        for line in self.line_ids:
            amount_bonus = self.compute_bonus_gross(line.employee_id, line.net_amount)
            line.amount = amount_bonus

    def _check_approval(self, state):
        """Check if target state is achievable."""
        for rec in self:
            is_hr_user = rec.env.user.has_group("hr.group_hr_user")
            is_bonus_manager = rec.env.user.has_group("hr_bonus.hr_bonus_group_manager")
            if state == "confirm":
                if not is_hr_user:
                    raise UserError(
                        _(
                            "Only a  HR Officer or  Bonus Manager can approve Bonus requests."
                        )
                    )

            if state == "payed":
                if not is_bonus_manager:
                    raise UserError(
                        _("Only an bonus manager can validate bonus requests.")
                    )

    def action_confirm(self):
        """Set state to confirm."""
        for rec in self:
            rec._check_approval("confirm")
            rec.state = "confirm"

    def action_payed(self):
        """Set state to pay."""
        for rec in self:
            rec._check_approval("payed")
            rec.state = "payed"

    def button_draft(self):
        self.write({"state": "draft"})


class HrBonusLine(models.Model):
    _name = "hr.bonus.line"
    _description = "Hr Bonus Line"

    employee_id = fields.Many2one("hr.employee", string="Employee")
    base_amount = fields.Float(string="Base", digits="Payroll")
    percent = fields.Float(string="Percent (%)")
    net_amount = fields.Float(string="NET", digits="Payroll")
    amount = fields.Float(string="Gross", digits="Payroll")
    bonus_id = fields.Many2one("hr.bonus", string="Bonus")

    @api.onchange("percent", "base_amount")
    def onchange_percent(self):
        if self.base_amount:
            if self.percent:
                self.net_amount = (self.base_amount * self.percent) / 100
            else:
                self.net_amount = self.base_amount

    @api.onchange("net_amount")
    def onchange_net_amount(self):
        self.amount = self.net_amount

    @api.constrains("employee_id")
    def _check_exist_employee_id(self):
        for record in self:
            if record.bonus_id.line_ids.filtered(
                lambda l: l.employee_id.id == record.employee_id.id
                and l.id != record.id
            ):
                raise ValidationError(
                    _("This employee %s already exist!" % record.employee_id.name)
                )

    @api.constrains("net_amount")
    def _check_net_amount(self):
        for record in self:
            if record.net_amount <= 0:
                raise ValidationError(
                    _(
                        "The Net of employee %s must be greater then 0"
                        % record.employee_id.name
                    )
                )


class HrSalaryRule(models.Model):
    _inherit = "hr.salary.rule"

    is_bonus = fields.Boolean(string="Is bonus")
    structure_ids = fields.Many2many(
        "hr.payroll.structure", string="Structures", required=1
    )

    @api.onchange("is_bonus")
    def onchange_bonus(self):
        """Set category condition and amount ."""
        if self.is_bonus:
            self.category_id = self.env.ref("hr_payroll.O_ALW").id
            self.condition_select = "python"
            self.amount_select = "code"
            self.sequence = 22

    @api.constrains("code")
    def _check_code(self):
        """Check code if contain '.'."""
        for rec in self:
            if rec.code.find(".") != -1:
                raise ValidationError(_('The Code should not contain "."'))

    def create_structure_rule(self, salary_rule):
        """Add rule to structure when create rule."""
        for structure in salary_rule.structure_ids:
            structure.rule_ids = [(4, salary_rule.id)]

    def write(self, vals):
        """Write the rule ."""
        if vals.get("is_bonus", False):
            self.structure_ids.write(vals)
        return super(HrSalaryRule, self).write(vals)

    @api.model
    def create(self, vals):
        """Create rule (type bonus)."""
        res = super(HrSalaryRule, self).create(vals)
        if res.is_bonus:
            self.create_structure_rule(res)
        return res

    @api.onchange("code")
    def onchange_code(self):
        """Change Code."""
        if self.code:
            self.condition_python = (
                "result = inputs.%s and inputs.%s.amount or False"
                % (self.code, self.code)
            )
            self.amount_python_compute = "result = inputs.%s.amount" % self.code
