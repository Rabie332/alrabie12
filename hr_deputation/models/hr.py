from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    deputation_balance = fields.Integer(
        string="Deputation Balance", compute="_compute_deputation_balance"
    )
    deputation_ids = fields.One2many(
        "hr.deputation", "employee_id", string="Deputation"
    )

    @api.model
    def initialize_deputation_stock(self):
        """Initialize deputation stock."""
        dep_setting = self.env["hr.deputation.setting"].search([], limit=1)
        obj_deputation_stock = self.env["hr.employee.deputation.stock"]
        deputation_stock = obj_deputation_stock.search([("employee_id", "=", self.id)])
        if dep_setting and not deputation_stock:
            deputation_available_stock = dep_setting.annual_balance
            deputation_stock.create(
                {
                    "deputation_available_stock": deputation_available_stock,
                    "current_stock": deputation_available_stock,
                    "employee_id": self.id,
                }
            )

            return True

    @api.depends("deputation_ids")
    def _compute_deputation_balance(self):
        """Get available stock value of deputation."""
        for rec in self:
            rec.deputation_balance = 0
            stock_line = self.env["hr.employee.deputation.stock"].search(
                [("employee_id", "=", rec.id)], limit=1
            )
            if stock_line:
                rec.deputation_balance = (
                    stock_line.deputation_available_stock
                    - stock_line.token_deputation_sum
                )

    def get_deputation_by_travel_date(self, date):
        """Get all deputation session for this employee in date : date.

        :param date:
        :return: objects browser with all deputation records
        """
        deputation_obj = self.env["hr.deputation"]
        deputation_ids = deputation_obj.sudo().search(
            [
                ("employee_id", "=", self.id),
                ("date_from_travel", "<=", date),
                ("date_to_travel", ">=", date),
            ]
        )
        return deputation_ids

    def get_deputation_by_date(self, date):
        """Get all deputation session for this employee in date : date.

        :param date:
        :return: objects browser with all deputation records
        """
        deputation_obj = self.env["hr.deputation"]
        deputation_ids = deputation_obj.sudo().search(
            [
                ("employee_id", "=", self.id),
                ("date_from", "<=", date),
                ("date_to", ">=", date),
            ]
        )
        return deputation_ids

    def action_confirm(self):
        """Create  deputation stock for this employee ."""
        res = super(HrEmployee, self).action_confirm()
        self.initialize_deputation_stock()
        return res


class HrEmployeeDeputationStock(models.Model):
    _name = "hr.employee.deputation.stock"
    _inherit = ["mail.thread"]
    _rec_name = "employee_id"
    _description = "Employee Deputation Stock"

    employee_id = fields.Many2one("hr.employee", string="Employee")
    deputation_available_stock = fields.Float(
        string="Deputation available stock", tracking=True
    )
    current_stock = fields.Float(
        string="Current Stock", compute="_compute_current_stock", store=1
    )
    token_deputation_sum = fields.Integer(string="Token Days")
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        readonly=1,
    )

    # ------------------------------------------------------------
    # Onchange methods
    # ------------------------------------------------------------
    @api.onchange("employee_id")
    def _onchange_employee_id(self):
        if self.employee_id:
            self.company_id = self.employee_id.company_id

    # ------------------------------------------------------------
    # Compute methods
    # ------------------------------------------------------------
    @api.depends("token_deputation_sum", "deputation_available_stock")
    def _compute_current_stock(self):
        """Calculate deputation current stock for employee ."""
        for rec in self:
            rec.current_stock = 0
            hr_deputation_setting = rec.env["hr.deputation.setting"].search([], limit=1)
            if rec.deputation_available_stock and not rec.token_deputation_sum:
                rec.current_stock = rec.deputation_available_stock
            if (
                rec.token_deputation_sum
                and not hr_deputation_setting.balance_deputation_no_specified
            ):
                rec.current_stock = (
                    rec.deputation_available_stock - rec.token_deputation_sum
                )
