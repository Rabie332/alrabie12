from odoo import _, api, fields, models


class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    hr_period_id = fields.Many2one(required=True)
    total_payslip = fields.Float(
        compute="_compute_total_payslip",
        string="Net",
        store=True,
        digits="Payroll",
    )
    old_total_payslip = fields.Float(
        string="Old Net",
        digits="Payroll",
        compute_sudo=True,
    )
    difference_old_new_payslip = fields.Float(
        compute="_compute_total_payslip",
        string="Difference",
        digits="Payroll",
        compute_sudo=True,
    )

    @api.depends("line_ids", "hr_period_id")
    def _compute_total_payslip(self):
        """Compute the total payslip,old payslip and the difference"""
        for payslip in self:
            payslip.total_payslip = sum(
                line.total
                for line in payslip.line_ids
                if line.category_id.code == "NET"
            )
            payslip.old_total_payslip = (
                payslip.env["hr.payslip"]
                .search(
                    [
                        ("employee_id", "=", payslip.employee_id.id),
                        ("date_from", "<", payslip.date_from),
                        ("state", "=", "done"),
                    ],
                    limit=1,
                    order="date_from desc",
                )
                .total_payslip
            )
            payslip.difference_old_new_payslip = abs(
                payslip.total_payslip - payslip.old_total_payslip
            )

    @api.model
    def get_worked_day_lines(self, contracts, date_from, date_to):
        """
        @param contract: Browse record of contracts
        @return: returns a list of dict containing the input that should be
                 applied for the given contract between date_from and date_to
        """
        res = super(HrPayslip, self).get_worked_day_lines(contracts, date_from, date_to)
        for work_day in res:
            if work_day.get("code", False) == "WORK100":
                contract = self.env["hr.contract"].browse(
                    int(work_day.get("contract_id", False))
                )
                # if get_worked_day_lines called from payslip run
                if not self.hr_period_id:
                    hr_period_id = self.env["hr.period"].search(
                        [("date_start", "=", date_from), ("date_end", "=", date_to)],
                        limit=1,
                    )
                else:
                    hr_period_id = self.hr_period_id
                if hr_period_id:
                    # Work days and Work hours of employee must
                    # be  Work days and Work hours of current period
                    work_day["number_of_days"] = hr_period_id.number_worked_days
                    work_day["number_of_hours"] = hr_period_id.number_worked_hours
                    # To calculate the difference date start of contract and date start
                    # of current period must be _in the same month and year
                    if (
                        hr_period_id.date_start
                        and hr_period_id.date_end
                        and (hr_period_id.date_start < contract.date_start)
                        and (hr_period_id.date_start.month == contract.date_start.month)
                        and (hr_period_id.date_start.year == contract.date_start.year)
                    ):
                        working_days = (
                            hr_period_id.date_end - contract.date_start
                        ).days + 1
                        work_day["number_of_days"] = working_days
                        # Work hours calculate form working
                        # days and hour per days of resource calendar
                        work_day["number_of_hours"] = (
                            working_days * contract.resource_calendar_id.hours_per_day
                        )
                    if contract and contract.date_end and contract.date_end < date_to:
                        working_days = ((contract.date_end - date_from).days) + 1

                        work_day["number_of_days"] = working_days
                        # Work hours calculate form working
                        # dayas and hour per days of resource calendar
                        work_day["number_of_hours"] = (
                            working_days * contract.resource_calendar_id.hours_per_day
                        )

        return res

    @api.onchange("company_id", "contract_id")
    def onchange_company_id(self):
        """Deactivate the original onchange to block the change of the period."""
        return []

    @api.onchange("contract_id")
    def onchange_contract_period(self):
        if self.contract_id.employee_id and self.contract_id:
            employee = self.contract_id.employee_id
            if self.hr_period_id:
                self.name = _("Salary Slip of %s for %s") % (
                    employee.name,
                    self.hr_period_id.name,
                )


class HrPayslipRun(models.Model):
    _inherit = "hr.payslip.run"

    total_slips = fields.Float(
        compute="_compute_total_slips", string="Total Salary", store=True
    )

    state = fields.Selection(selection_add=[("done", "Done"), ("close", "Close")])
    hr_period_id = fields.Many2one(
        "hr.period",
        states={"close": [("readonly", 1)], "done": [("readonly", 1)]},
    )
    category_ids = fields.Many2many(
        "hr.employee.category",
        readonly=1,
        states={"draft": [("readonly", 0)]},
    )

    @api.depends("slip_ids", "slip_ids.total_payslip")
    def _compute_total_slips(self):
        for payslip_run in self:
            payslip_run.total_slips = sum(payslip_run.slip_ids.mapped("total_payslip"))

    def payslip_run_done(self):
        for payslip_run in self:
            for payslip in payslip_run.slip_ids.filtered(
                lambda payslip: payslip.state == "draft"
            ):
                payslip.action_payslip_done()
            payslip_run.state = "done"

    def print_xls_report(self):
        """Print Payslip run report XlSX."""
        data = {"ids": [self.id], "form": self.read([])[0]}
        return self.env.ref("hr_payroll_base.payslip_run_report_xlsx").report_action(
            self, data=data
        )

    def draft_payslip_run(self):
        super(HrPayslipRun, self).draft_payslip_run()
        self.slip_ids.write({"state": "draft"})
