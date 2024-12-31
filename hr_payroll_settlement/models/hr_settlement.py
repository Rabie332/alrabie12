from odoo import api, fields, models


class HrSettlement(models.Model):
    _name = "hr.settlement"
    _inherit = "request"
    _description = "Settlement"

    @api.model
    def _get_domain_period(self):
        """Get current period."""
        today = fields.date.today()
        periods = (
            self.env["hr.period"]
            .search(
                [
                    "|",
                    ("date_start", "<=", today),
                    ("date_start", ">=", today),
                    ("date_end", ">=", today),
                    ("state", "=", "open"),
                ]
            )
            .ids
        )
        return [("id", "in", periods)]

    @api.model
    def get_default_period_id(self):
        today = fields.date.today()
        period = self.env["hr.period"].search(
            [
                ("date_start", "<=", today),
                ("date_end", ">=", today),
                ("state", "=", "open"),
            ],
            limit=1,
        )
        return period.id if period else False

    period_id = fields.Many2one(
        "hr.period",
        domain=_get_domain_period,
        default=get_default_period_id,
        string="Specific period",
        required=1,
        readonly=1,
        states={"draft": [("readonly", 0)]},
    )
    amount = fields.Float(string="Amount", readonly=1)
    amount_deduction = fields.Float(
        string="Amount Deduction", readonly=1, states={"draft": [("readonly", 0)]}
    )
    amount_addition = fields.Float(
        string="Amount Addition", readonly=1, states={"draft": [("readonly", 0)]}
    )
    days = fields.Float(string="Days", readonly=1, states={"draft": [("readonly", 0)]})
    notes = fields.Text(string="Notes", readonly=1, states={"draft": [("readonly", 0)]})
    type = fields.Selection(
        [("deduction", "Deduction"), ("addition", "Addition")],
        string="Settlement Type",
        required=1,
        readonly=1,
        states={"draft": [("readonly", 0)]},
    )
    compute_method = fields.Selection(
        [
            ("basic_salary", "Basic salary"),
            ("net_salary", "Net salary"),
            ("days_absence", "Days absence"),
            ("days_delay", "Days delay"),
            ("amount", "Amount"),
        ],
        string="Compute Method",
        required=1,
        readonly=1,
        states={"draft": [("readonly", 0)]},
    )
    days = fields.Float(
        string="Days Number", readonly=1, default=1, states={"draft": [("readonly", 0)]}
    )
    refuse_reason = fields.Text("Refuse Reason", readonly=1)
    active = fields.Boolean("Active", default=True)
    company_id = fields.Many2one("res.company", default=lambda self: self.env.company)
    # ------------------------------------------------------------
    # ORM methods
    # ------------------------------------------------------------

    @api.model
    def create(self, vals):
        """Add sequence."""
        settlement = super(HrSettlement, self).create(vals)
        if settlement:
            settlement.name = self.env["ir.sequence"].next_by_code("hr.settlement.seq")
        return settlement

    def name_get(self):
        res = []
        for loan in self:
            res.append((loan.id, (loan.name)))
        return res

    def _sync_employee_details(self):
        for request in self:
            super(HrSettlement, request)._sync_employee_details()
            if request.employee_id and request.employee_id.company_id:
                request.company_id = request.employee_id.company_id.id

    # ------------------------------------------------------------
    # Compute  methods
    # ------------------------------------------------------------
    @api.depends("stage_id")
    def _compute_display_button(self):
        for settlement in self:
            super(HrSettlement, settlement)._compute_display_button()
            settlement.display_button_send = False
            if settlement.state == "draft" and (
                settlement.env.user.has_group(
                    "hr_payroll_settlement.group_hr_payroll_settlement_manager"
                )
            ):
                settlement.display_button_send = True

    # ------------------------------------------------------------
    # Onchange  methods
    # ------------------------------------------------------------

    @api.onchange(
        "period_id",
        "employee_id",
        "type",
        "compute_method",
        "days",
        "amount_addition",
        "amount_deduction",
    )
    def _onchange_period_id(self):
        """Get all settlements for employee on given period."""
        if self.period_id and self.employee_id and self.type and self.compute_method:
            contract_id = self.employee_id.contract_id
            # calculate number of days of period
            period_days = (
                self.period_id.number_worked_days
                and self.period_id.number_worked_days
                or 1
            )
            (
                basic_salary,
                gross_salary,
                net_salary,
            ) = self.employee_id._get_employee_info(contract_id)
            factor = 1.0
            if self.type == "deduction":
                factor = -1.0
            if self.compute_method == "basic_salary":
                self.amount = basic_salary / period_days * self.days * factor
            elif self.compute_method == "net_salary":
                self.amount = net_salary / period_days * self.days * factor
            elif self.compute_method == "amount":
                if self.type == "deduction":
                    self.amount = self.amount_deduction * factor
                else:
                    self.amount = self.amount_addition * factor
            elif self.compute_method == "days_absence":
                # Claculate amount from basic salary and allowances (GROSS)
                self.amount = gross_salary / period_days * self.days * factor
            elif self.compute_method == "days_delay":
                # Clalculate amount from basic salary
                self.amount = basic_salary / period_days * self.days * factor

    def get_approvals(self):
        """Return stage name and approver and his signature."""
        for request in self:
            stages = request.sudo().get_approvals_details()
            approved_stages = []
            for stage in stages:
                approver = stages[stage]["approver"]
                stage_obj = request.env["request.stage"].browse(
                    stages[stage]["stage_id"]
                )

                if stage_obj and stage_obj.appears_in_settlement_report:
                    vals = {
                        "stage": stage,
                        "approver_name": approver.name,
                        "signature": False,
                        "sequence": stage_obj.sequence,
                        "date": stages[stage]["date"].strftime("%Y-%m-%d")
                        if stages[stage]["date"]
                        else "",
                    }
                    if approver:
                        vals["signature"] = approver.digital_signature
                    approved_stages.append(vals)
            return sorted(approved_stages, key=lambda i: i["sequence"])
