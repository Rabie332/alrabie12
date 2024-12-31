from dateutil.relativedelta import relativedelta
from lxml import etree

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HrTraining(models.Model):
    _name = "hr.training"
    _inherit = "request"
    _description = "Training"

    name = fields.Char(
        readonly=1, states={"draft": [("readonly", 0)]}, string="Course Name"
    )
    date_from = fields.Date(
        string="Date From", required=1, readonly=1, states={"draft": [("readonly", 0)]}
    )
    date_to = fields.Date(
        string="Date To", required=1, readonly=1, states={"draft": [("readonly", 0)]}
    )
    duration = fields.Float(string=" Duration", compute="_compute_duration", store=True)
    training_center_id = fields.Many2one(
        "hr.training.center",
        string="Training Center Name",
        readonly=1,
        states={"draft": [("readonly", 0)]},
    )
    training_center = fields.Char("Training Center")
    type = fields.Selection(
        [("internal", "Internal"), ("external", "External")],
        string="Training Type",
        default="internal",
        readonly=1,
        states={"draft": [("readonly", 0)]},
    )
    transportation_type = fields.Selection(
        [("overland", "Overland"), ("air_travel", "Air travel")],
        string="Transportation means",
        default="air_travel",
        readonly=1,
        states={"draft": [("readonly", 0)]},
    )
    travel_days = fields.Selection(
        [("1", "1"), ("2", "2"), ("3", "3"), ("4", "4")],
        string="Travel days",
        readonly=1,
    )
    total = fields.Float(
        string="Total amount", readonly=1, states={"draft": [("readonly", 0)]}
    )
    country_id = fields.Many2one(
        "res.country",
        string="Country",
        readonly=1,
        states={"draft": [("readonly", 0)]},
        default=lambda self: self.env["res.country"].search(
            [("code", "=", "SA")], limit=1
        ),
    )
    city_id = fields.Many2one(
        "res.city", string="City ", readonly=1, states={"draft": [("readonly", 0)]}
    )
    city = fields.Char("City", readonly=1, states={"draft": [("readonly", 0)]})
    program_training = fields.Text(
        string="Training Program", readonly=1, states={"draft": [("readonly", 0)]}
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
        readonly=1,
        states={"draft": [("readonly", 0)]},
    )
    number = fields.Char(string="Job number", readonly=1)
    refuse_reason = fields.Char(string="Refusal reason")
    description = fields.Text(
        string="Description", readonly=1, states={"draft": [("readonly", 0)]}
    )
    course_outcomes = fields.Text(
        "Course Outcomes", readonly=1, states={"draft": [("readonly", 0)]}
    )
    training_allowance = fields.Float(
        string="Training allowance", readonly=1, tracking=True
    )
    fees_amount = fields.Float(
        string="Fees Amount", readonly=1, states={"draft": [("readonly", 0)]}
    )
    hosing = fields.Boolean(
        string="Hosing", readonly=1, states={"draft": [("readonly", 0)]}
    )
    food = fields.Boolean(
        string="Food", readonly=1, states={"draft": [("readonly", 0)]}
    )
    transport = fields.Boolean(
        string="Transport", readonly=1, states={"draft": [("readonly", 0)]}
    )
    attachment_ids = fields.Many2many(
        "ir.attachment",
        string="Attachments",
        readonly=1,
        states={"draft": [("readonly", 0)]},
    )
    active = fields.Boolean("Active", default=True)
    include_ticket_total_amount = fields.Boolean(
        string="Include ticket price in total amount",
        readonly=1,
        states={"draft": [("readonly", 0)]},
    )
    ticket_price = fields.Float(
        string="Ticket Price", readonly=1, states={"draft": [("readonly", 0)]}
    )
    read_reviewed_policies_regulations = fields.Boolean(
        "I have read and reviewed the policies and regulations",
        readonly=1,
        states={"draft": [("readonly", 0)]},
    )
    is_paid = fields.Boolean(string="Is paid")
    canceled = fields.Boolean(default=False, copy=False)
    display_button_set_to_draft = fields.Boolean(
        "Display set to draft button", compute="_compute_display_button"
    )
    # ------------------------------------------------------------
    # Compute methods
    # ------------------------------------------------------------

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

                if stage_obj and stage_obj.appears_in_training_report:
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

    @api.model
    def create(self, vals):
        training = super(HrTraining, self).create(vals)
        if training:
            for attachment in training.attachment_ids.filtered(
                lambda attachment: not attachment.res_id
            ):
                attachment.res_id = training.id
        return training

    @api.depends("date_from", "date_to")
    def _compute_duration(self):
        for training in self:
            if training.date_from and training.date_to:
                date_from = fields.Date.from_string(training.date_from)
                date_to = fields.Date.from_string(training.date_to)
                training.duration = (date_to - date_from).days + 1

    @api.depends("stage_id")
    def _compute_display_button(self):
        for training in self:
            users = training._get_approvers()
            # Display set to draft button
            training.display_button_set_to_draft = False
            if training.state == "in_progress" and (
                training.env.user.id in users
                or training.env.user.has_group("hr_training.group_training_managment")
            ):
                training.display_button_set_to_draft = True
            training.display_button_refuse = False
            training.display_button_accept = False
            training.display_button_send = False
            if training.state == "draft" and (
                (training.create_uid and training.create_uid.id == training.env.uid)
                or training.env.user.has_group("hr_training.group_training_managment")
            ):
                training.display_button_send = True
            elif training.state == "in_progress" and (
                training.env.uid in users
                or training.env.user.has_group("hr_training.group_training_managment")
            ):
                training.display_button_accept = True
                training.display_button_refuse = True

    def set_to_draft(self):
        """Set to draft."""
        for training in self:
            training.stage_id = training._get_next_stage(stage_type="default")
            training._onchange_stage_id()
            training._make_done_activity()
            training.activity_schedule(
                "hr_training.mail_hr_training_set_to_draft",
                user_id=training.create_uid.id,
            )

    # ------------------------------------------------------------
    # Constraint methods
    # ------------------------------------------------------------

    def training_intersection(self, date_from, date_to, employee_id):
        """Check if employee_id have training between date_from, date_to."""
        search_domain = [
            ("employee_id", "=", employee_id),
            ("state", "!=", "cancel"),
            ("id", "!=", self.id),
        ]
        for rec in self.env["hr.training"].sudo().search(search_domain):
            if (
                rec.date_from <= date_from <= rec.date_to
                or rec.date_from <= date_to <= rec.date_to
                or date_from <= rec.date_from <= date_to
                or date_from <= rec.date_to <= date_to
            ):
                return True
        return False

    @api.constrains("date_from", "date_to")
    def _check_dates(self):
        for training in self:
            if (
                training.date_from
                and training.date_to
                and training.date_from > training.date_to
            ):
                raise ValidationError(
                    _(
                        "The start date of the course should be "
                        "less than the date of the end of the course"
                    )
                )
            # Show error message if there is training intersection
            if training.training_intersection(
                training.date_from, training.date_to, training.employee_id.id
            ):
                raise ValidationError(_("There is an overlap of dates with a training"))

    @api.constrains("duration", "travel_days")
    def _check_duration(self):
        """Check if duration + travel days depassed annual balance."""
        hr_training_setting = self.env["hr.training.setting"].search([], limit=1)
        if (
            not hr_training_setting.balance_training_no_specified
            and self.employee_id
            and self.duration
        ):
            if self.employee_id.training_balance < (
                self.duration + int(self.travel_days or 0)
            ):
                raise ValidationError(
                    _("The annual training balance has been exceeded!")
                )

    # ------------------------------------------------------------
    # Onchange methods
    # ------------------------------------------------------------

    @api.onchange(
        "duration",
        "training_allowance",
        "travel_days",
        "food",
        "hosing",
        "transport",
        "fees_amount",
        "include_ticket_total_amount",
        "ticket_price",
    )
    def _onchange_days(self):
        """Compute Amount and total."""
        # to do get training allowance with job position
        hr_training_setting = self.env["hr.training.allowance"].search([], limit=1)
        food = transport = hosing = 0
        # compute total and amount with duration and travel_days
        days = self.duration + int(self.travel_days or 0)
        amount = self.training_allowance * days
        # remove food amount of from amount
        if self.food:
            food = amount / 100 * hr_training_setting.food
        # remove transport amount of from amount
        if self.transport:
            transport = amount / 100 * hr_training_setting.transport
        # remove hosing amount of from amount
        if self.hosing:
            hosing = amount / 100 * hr_training_setting.hosing
        amount -= food + transport + hosing
        # add fees_amount to total price
        self.total = amount + self.fees_amount
        # add ticket price
        if self.include_ticket_total_amount:
            self.total += self.ticket_price

    @api.onchange("type")
    def _onchange_type(self):
        # calcul training allowance
        if self.type:
            if self.type == "internal":
                self.city = False
                self.country_id = self.env["res.country"].search(
                    [("code", "=", "SA")], limit=1
                )
            if self.type == "external":
                self.country_id = False
                self.city = False
        training_allowance_obj = self.env["hr.training.allowance"]
        # get training allowance with job position
        if self.type:
            # get training_allowance value from setting
            (
                training_allowance,
                transport_amount,
            ) = training_allowance_obj.get_training_allowance_amount(self.type, self)
            self.training_allowance = training_allowance

    @api.onchange("employee_id")
    def _onchange_employee_id(self):
        super(HrTraining, self)._onchange_employee_id()
        if self.employee_id:
            self.number = self.employee_id.number
            # get training value from setting
            training_allowance_obj = self.env["hr.training.allowance"]
            (
                training_amount,
                training_transport,
            ) = training_allowance_obj.get_training_allowance_amount(self.type, self)
            self.training_allowance = training_amount

    @api.onchange("country_id")
    def onchange_country_id(self):
        """Calculate travel days from training settings."""
        deputation_allowance_obj = self.env["hr.training.allowance"]
        # take travel days for first location
        if self.country_id and self.employee_id:
            self.travel_days = deputation_allowance_obj.get_travel_days(
                self.country_id, self
            )
        # nothing to do it
        else:
            pass

    # ------------------------------------------------------------
    #  Methods
    # ------------------------------------------------------------

    @api.model
    def update_training_stock(self):
        """Update stock of employees every worked year."""
        employees = self.env["hr.employee"].search([])
        today_date = fields.Date.from_string(fields.Date.today())
        training_setting = self.env["hr.training.setting"].search([], limit=1)
        # Update stock of training for employee every year
        for employee in employees:
            stock_line = self.env["hr.employee.training.stock"].search(
                [("employee_id", "=", employee.id)]
            )
            if training_setting and training_setting.annual_balance > 0 and stock_line:
                training_available_stock = training_setting.annual_balance
                if (
                    employee.date_direct_action
                    and employee.date_direct_action < today_date
                    and relativedelta(
                        today_date,
                        employee.date_direct_action,
                    ).months
                    == 0
                    and relativedelta(today_date, employee.date_direct_action).days == 0
                ):
                    stock_line.write(
                        {
                            "training_available_stock": stock_line.training_available_stock
                            + training_available_stock
                            if training_setting.accumulative_balance
                            else training_available_stock,
                            "current_stock": training_available_stock,
                            "token_training_sum": 0,
                        }
                    )

    @api.model
    def initialize_training_stock(self):
        """Initialize training stock."""
        training_setting = self.env["hr.training.setting"].search([], limit=1)
        obj_training_stock = self.env["hr.employee.training.stock"]
        for employee in self.env["hr.employee"].search([]):
            training_stock = obj_training_stock.search(
                [("employee_id", "=", employee.id)]
            )
            if (
                training_setting
                and training_setting.annual_balance > 0
                and not training_stock
            ):
                training_available_stock = training_setting.annual_balance
                training_stock.sudo().create(
                    {
                        "training_available_stock": training_available_stock,
                        "current_stock": training_available_stock,
                        "employee_id": employee.id,
                    }
                )

    def action_accept(self):
        """Accept the request and Send it to be approved by the right users."""
        for rec in self:
            super(HrTraining, rec).action_accept()
            if rec.state == "done":
                stock_line = (
                    self.env["hr.employee.training.stock"]
                    .sudo()
                    .search([("employee_id", "=", rec.employee_id.id)], limit=1)
                )
                if stock_line:
                    stock_line.sudo().token_training_sum += rec.duration + int(
                        rec.travel_days or 0
                    )

    def action_send(self):
        """Send the request to be approved by the right users."""
        for training in self:
            if not training.read_reviewed_policies_regulations:
                raise ValidationError(
                    _("You must read and reviewed the policies regulations")
                )
            super(HrTraining, self).action_send()

    # ------------------------------------------------------------
    # ORM methods
    # ------------------------------------------------------------

    @api.model
    def fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        """fields_view_get to remove create and edit and delete from menu training."""
        res = super(HrTraining, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu
        )
        doc = etree.XML(res["arch"])
        if self.env.context.get("no_display_create"):
            for node in doc.xpath("//tree"):
                node.set("create", "0")
            for node in doc.xpath("//form"):
                node.set("create", "0")
            for node in doc.xpath("//kanban"):
                node.set("create", "0")
        res["arch"] = etree.tostring(doc, encoding="unicode")
        return res

    def action_cancel(self):
        for training in self:
            if training.state == "done":

                stock_line = (
                    training.env["hr.employee.training.stock"]
                    .sudo()
                    .search([("employee_id", "=", training.employee_id.id)], limit=1)
                )
                if stock_line:
                    stock_line.token_training_sum -= training.duration + int(
                        training.travel_days or 0
                    )
            training.stage_id = training._get_next_stage(stage_type="cancel")
            training._onchange_stage_id()
            training.canceled = True
