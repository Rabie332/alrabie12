from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    training_balance = fields.Integer(
        string="Training Balance", compute="_compute_training_balance"
    )
    training_ids = fields.One2many("hr.training", "employee_id", string="Training")

    @api.model
    def initialize_training_stock(self):
        """Initialize training stock."""
        training_setting = self.env["hr.training.setting"].search([], limit=1)
        obj_training_stock = self.env["hr.employee.training.stock"]
        training_stock = obj_training_stock.search([("employee_id", "=", self.id)])
        if training_setting and not training_stock:
            training_available_stock = training_setting.annual_balance
            training_stock.create(
                {
                    "training_available_stock": training_available_stock,
                    "current_stock": training_available_stock,
                    "employee_id": self.id,
                }
            )

            return True

    @api.depends("training_ids")
    def _compute_training_balance(self):
        """Get available stock value of training."""
        for rec in self:
            rec.training_balance = 0
            stock_line = self.env["hr.employee.training.stock"].search(
                [("employee_id", "=", rec.id)], limit=1
            )
            if stock_line:
                rec.training_balance = (
                    stock_line.training_available_stock - stock_line.token_training_sum
                )

    def get_training_by_travel_date(self, date):
        """Get all training session for this employee in date : date.

        :param date:
        :return: objects browser with all training records
        """
        training_obj = self.env["hr.training"]
        training_ids = training_obj.sudo().search(
            [
                ("employee_id", "=", self.id),
                ("date_from_travel", "<=", date),
                ("date_to_travel", ">=", date),
            ]
        )
        return training_ids

    def get_training_by_date(self, date):
        """Get all training session for this employee in date : date.

        :param date:
        :return: objects browser with all training records
        """
        training_obj = self.env["hr.training"]
        training_ids = training_obj.sudo().search(
            [
                ("employee_id", "=", self.id),
                ("date_from", "<=", date),
                ("date_to", ">=", date),
            ]
        )
        return training_ids

    @api.model
    def create(self, vals):
        employee = super(HrEmployee, self).create(vals)
        if employee:
            employee.initialize_training_stock()
        return employee


class HrEmployeetrainingStock(models.Model):
    _name = "hr.employee.training.stock"
    _inherit = ["mail.thread"]
    _rec_name = "employee_id"
    _description = "Employee training Stock"

    employee_id = fields.Many2one("hr.employee", string="Employee")
    training_available_stock = fields.Float(
        string="Training available stock", tracking=True
    )
    current_stock = fields.Float(
        string="Current Stock", compute="_compute_current_stock", store=1
    )
    token_training_sum = fields.Integer(string="Token Days")
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
    @api.depends("token_training_sum", "training_available_stock")
    def _compute_current_stock(self):
        """Calculate training current stock for employee ."""
        for rec in self:
            rec.current_stock = 0
            hr_training_setting = rec.env["hr.training.setting"].search([], limit=1)
            if rec.training_available_stock and not rec.token_training_sum:
                rec.current_stock = rec.training_available_stock
            if (
                rec.token_training_sum
                and not hr_training_setting.balance_training_no_specified
            ):
                rec.current_stock = (
                    rec.training_available_stock - rec.token_training_sum
                )
