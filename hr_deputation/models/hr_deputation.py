from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta
from lxml import etree

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HrDeputation(models.Model):
    _name = "hr.deputation"
    _inherit = "request"
    _order = "id desc"
    _description = "Deputation"

    active = fields.Boolean(default=True)
    is_paid = fields.Boolean(string="Is paid")
    country_id = fields.Many2one(
        "res.country",
        string="Country",
        default=lambda self: self.env["res.country"].search(
            [("code", "=", "SA")], limit=1
        ),
        readonly=1,
    )
    job_id = fields.Many2one("hr.job", string="Job", readonly=1)
    city_id = fields.Many2one(
        "res.city", string="City", readonly=1, states={"draft": [("readonly", 0)]}
    )
    date_from = fields.Date(
        string="Date from", readonly=1, states={"draft": [("readonly", 0)]}
    )
    date_to = fields.Date(
        string="Date to", readonly=1, states={"draft": [("readonly", 0)]}
    )
    note = fields.Text(string="Notes", readonly=1, states={"draft": [("readonly", 0)]})
    hosing = fields.Boolean(
        string="Hosing", readonly=1, states={"draft": [("readonly", 0)]}
    )
    food = fields.Boolean(
        string="Food", readonly=1, states={"draft": [("readonly", 0)]}
    )
    transport = fields.Boolean(
        string="Transport", readonly=1, states={"draft": [("readonly", 0)]}
    )
    transportation_type = fields.Selection(
        [("overland", "Overland"), ("air_travel", "Air travel")],
        string="Transportation means",
        default="air_travel",
        readonly=1,
        states={"draft": [("readonly", 0)]},
    )
    type = fields.Selection(
        [("internal", "Internal"), ("external", "External")],
        string="Type",
        default="internal",
        readonly=1,
        states={"draft": [("readonly", 0)]},
    )
    location_ids = fields.One2many(
        "hr.deputation.location",
        "deputation_id",
        string="Locations",
        readonly=1,
        states={"draft": [("readonly", 0)]},
    )
    task_name = fields.Text(
        string="Task", required=1, readonly=1, states={"draft": [("readonly", 0)]}
    )
    duration = fields.Integer(
        string="Duration", readonly=1, compute="_compute_duration", store=True
    )
    request_type_id = fields.Many2one(required=1, string="Deputation Type")

    travel_days = fields.Selection(
        [("1", "1"), ("2", "2"), ("3", "3"), ("4", "4")],
        string="Travel days",
        readonly=1,
    )
    deputation_allowance = fields.Float(
        string="Deputation allowance", readonly=1, tracking=True
    )
    total = fields.Float(string="Total amount", readonly=1)
    attachment_ids = fields.Many2many(
        "ir.attachment",
        string="Attachments",
        readonly=1,
        states={"draft": [("readonly", 0)]},
    )
    reason = fields.Text(
        string="Reason", readonly=1, states={"draft": [("readonly", 0)]}
    )
    distance = fields.Float(
        string="Distance", readonly=1, states={"draft": [("readonly", 0)]}
    )
    date_from_travel = fields.Date(
        string="Deputation Travel Date", compute="_compute_dates_travel", store=1
    )
    date_to_travel = fields.Date(
        string="Deputation Date Return", compute="_compute_dates_travel", store=1
    )
    travel_days_setting = fields.Selection(
        [
            ("before_deputation", "Before Deputation"),
            ("after_deputation", "After Deputation"),
        ],
        default="before_deputation",
        string="Travel Day Date Settings",
        readonly=1,
        states={"draft": [("readonly", 0)]},
    )
    display_travel_dates = fields.Boolean(compute="_compute_display_travel_dates")
    color = fields.Integer("Color Index")
    fees_amount = fields.Float(
        string="Fees Amount", readonly=1, states={"draft": [("readonly", 0)]}
    )
    need_fees = fields.Boolean(
        string="Need Fees", readonly=1, states={"draft": [("readonly", 0)]}
    )
    display_button_cancel = fields.Boolean(
        compute="_compute_display_button_cancel", string="Display Button Cancel"
    )
    display_button_extend = fields.Boolean(
        compute="_compute_display_button_extend", string="Display Button Extend"
    )
    display_button_cut = fields.Boolean(
        compute="_compute_display_button_cut", string="Display Button Cut"
    )
    deputation_extension_ids = fields.One2many(
        "hr.deputation.extension", "deputation_id", string="Extension"
    )
    extension_duration = fields.Integer(
        string="Extension Duration", compute="_compute_extension_duration", store=True
    )
    is_cut = fields.Boolean(string="Is Cut", compute="_compute_is_cut")
    is_started = fields.Boolean(string="Is Started", compute="_compute_is_started")
    is_finished = fields.Boolean(string="Is Finished", compute="_compute_is_finished")
    is_extended = fields.Boolean(string="Is Extended", compute="_compute_is_extended")
    ticket_price = fields.Float(
        string="Ticket Price", readonly=1, states={"draft": [("readonly", 0)]}
    )
    include_ticket_total_amount = fields.Boolean(
        string="Include ticket price in total amount",
        readonly=1,
        states={"draft": [("readonly", 0)]},
    )
    kilometer_amount = fields.Float(
        string="kilometer Amount",
        compute="_compute_kilometer_amount",
        compute_sudo=True,
    )
    kilometer_amount_overland = fields.Float(
        string="kilometer Amount Overland", compute="_compute_kilometer_amount", store=1
    )
    display_ticket_amount = fields.Boolean(
        string="Display Ticket Amount", compute="_compute_kilometer_amount", store=1
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
    read_reviewed_policies_regulations = fields.Boolean(
        "I have read and reviewed the policies and regulations",
        readonly=1,
        states={"draft": [("readonly", 0)]},
    )
    canceled = fields.Boolean(default=False, copy=False)
    ticket_type = fields.Selection(
        [("economic", "Economic"), ("business", "Business")],
        "Ticket Type",
        readonly=1,
        states={"draft": [("readonly", 0)]},
    )
    duration_holiday_days = fields.Float(
        string="Duration holiday days",
        compute="_compute_duration_holiday_days",
        store=True,
    )
    amount_holidays = fields.Float(string="Holiday amount", readonly=1)
    amount_normal_days = fields.Float(string="Normal days amount", readonly=1)
    show_kilometer_amount = fields.Boolean(
        string="Show kilometer amount",
        compute="_compute_show_kilometer_amount",
        store=1,
    )

    # ------------------------------------------------------------
    # Compute methods
    # ------------------------------------------------------------
    @api.depends("stage_id")
    def _compute_display_button(self):
        for rec in self:
            users = rec._get_approvers()
            rec.display_button_refuse = False
            rec.display_button_accept = False
            rec.display_button_send = False
            rec.display_button_previous = False
            if rec.state == "draft" and (
                (rec.create_uid and rec.create_uid.id == rec.env.uid)
                or rec.env.user.has_group("hr_deputation.group_hr_deputation_user")
            ):
                rec.display_button_send = True
            elif rec.state == "in_progress" and (
                rec.env.uid in users
                or rec.env.user.has_group("hr_deputation.group_hr_deputation_user")
            ):
                rec.display_button_accept = True
                rec.display_button_refuse = True
                rec.display_button_previous = True

    @api.depends("distance")
    def _compute_show_kilometer_amount(self):
        for deputation in self:
            deputation_allowance = deputation.env[
                "hr.deputation.allowance"
            ].get_allowance(deputation)
            deputation.show_kilometer_amount = False
            if (
                len(deputation_allowance.deputation_kilometer_ids)
                and deputation_allowance.deputation_setting_id.deputation_with_kilometer
                and deputation.transportation_type == "overland"
            ):
                deputation.show_kilometer_amount = True

    @api.depends("distance")
    def _compute_kilometer_amount(self):
        """Check if the deputation can be cut or not."""
        for rec in self:
            hr_deputation_allowance = rec.env["hr.deputation.allowance"].search(
                [], limit=1
            )
            rec.kilometer_amount = (
                hr_deputation_allowance.get_kilometer_amount(rec)
                if hr_deputation_allowance.deputation_setting_id.deputation_with_kilometer
                else 0
            )
            rec.display_ticket_amount = False
            kilometer_amount_overland, deputation_allowance = self.env[
                "hr.deputation.allowance"
            ].get_deputation_allowance_kilometer_amount(rec)

            rec.kilometer_amount_overland = kilometer_amount_overland
            rec.display_ticket_amount = True if deputation_allowance else False

    @api.onchange("kilometer_amount_overland")
    def _onchange_kilometer_amount_overland(self):
        if self.kilometer_amount_overland and self.transportation_type == "overland":
            self.ticket_price = 0

    def _compute_display_button_cut(self):
        """Calcul Kilometer amount from setting."""
        for rec in self:
            rec.display_button_cut = False
            if (
                rec.state == "done"
                and (
                    rec.employee_id.user_id.id == self._uid
                    or rec.create_uid.id == self._uid
                    or rec.env.user.has_group("hr_deputation.group_hr_deputation_user")
                )
                and not rec.is_cut
                and rec.is_started
                and not rec.is_extended
                and not rec.is_finished
            ):
                rec.display_button_cut = True

    @api.depends(
        "deputation_extension_ids.new_duration", "deputation_extension_ids.state"
    )
    def _compute_extension_duration(self):
        """Calculate extension duration."""
        for rec in self:
            duration = 0
            for extension in rec.deputation_extension_ids:
                if extension.state == "done":
                    duration += extension.new_duration
            rec.extension_duration = duration

    def _compute_is_cut(self):
        """Check if the deputation have a pending or completed holidays cut."""
        for rec in self:
            rec.is_cut = False
            deputation_cancellation = self.env["hr.deputation.cut"].search(
                [("deputation_id", "=", rec.id), ("state", "!=", "cancel")]
            )
            if deputation_cancellation:
                rec.is_cut = True

    def _compute_is_started(self):
        """Compute field is_started:
        check current date is superior than the deputation's starting date."""
        for rec in self:
            rec.is_started = False
            if rec.date_from and rec.date_from <= datetime.today().date():
                rec.is_started = True

    def _compute_is_finished(self):
        """Compute field is_finished:
        check current date is superior than the holiday's finishing date."""
        for rec in self:
            rec.is_finished = False
            if rec.date_to and rec.date_to <= datetime.today().date():
                rec.is_finished = True

    def _compute_is_extended(self):
        """Check if the deputation have a pending or completed extension leave."""
        for rec in self:
            rec.is_extended = False
            for deputation_extension in rec.deputation_extension_ids:
                deputation_cut = self.env["hr.deputation.cut"].search(
                    [
                        ("deputation_id", "=", deputation_extension.id),
                        ("state", "!=", "done"),
                    ]
                )
                if deputation_extension.state != "cancel" and deputation_cut:
                    rec.is_extended = True

    def _compute_display_button_cancel(self):
        """Check if the deputation can be cancelled or not."""
        for rec in self:
            display_button_cancel = False
            deputation_cancel_count = rec.env[
                "hr.deputation.cancellation"
            ].search_count(
                [
                    ("deputation_id", "=", rec.id),
                    ("employee_id", "=", rec.employee_id.id),
                    ("state", "!=", "cancel"),
                ]
            )
            if (
                rec.state in ["done"]
                and rec.date_from
                and rec.date_from > datetime.today().date()
                and (
                    rec.employee_id.user_id.id == rec._uid
                    or rec.env.user.has_group("hr_deputation.group_hr_deputation_user")
                )
                and deputation_cancel_count == 0
            ):
                display_button_cancel = True
            rec.display_button_cancel = display_button_cancel

    def _compute_display_button_extend(self):
        """Check if the deputation can be extended or not."""
        for rec in self:
            display_button_extend = False
            deputation_extend_count = rec.env["hr.deputation.extension"].search_count(
                [
                    ("deputation_id", "=", rec.id),
                    ("employee_id", "=", rec.employee_id.id),
                    ("state", "!=", "cancel"),
                ]
            )
            if (
                rec.state in ["done"]
                and rec.date_from <= datetime.today().date()
                and rec.date_to >= datetime.today().date()
                and (
                    rec.employee_id.user_id.id == self._uid
                    or rec.env.user.has_group("hr_deputation.group_hr_deputation_user")
                )
                and not rec.is_cut
                and deputation_extend_count == 0
            ):
                display_button_extend = True
            rec.display_button_extend = display_button_extend

    def _compute_display_travel_dates(self):
        """Display date from travel and date to travel."""
        for record in self:
            setting = record.env["hr.deputation.setting"].search([], limit=1)
            record.display_travel_dates = setting.deputation_with_travel_dates

    @api.depends("date_from", "date_to", "travel_days", "travel_days_setting")
    def _compute_dates_travel(self):
        """Calculate date from travel and date to travel."""
        for record in self:
            record.date_from_travel = record.date_from
            record.date_to_travel = record.date_to
            # travel days == 1
            if int(record.travel_days) == 1:
                if (
                    record.travel_days_setting == "before_deputation"
                    and record.date_from
                ):
                    record.date_from_travel = fields.Date.from_string(
                        record.date_from
                    ) - relativedelta(days=1)
                if record.travel_days_setting == "after_deputation" and record.date_to:
                    record.date_to_travel = fields.Date.from_string(
                        record.date_to
                    ) + relativedelta(days=1)
            # travel days == 2 or 4 or 6
            if int(record.travel_days) % 2 == 0:
                days = int((int(record.travel_days)) / 2)
                if record.date_from:
                    record.date_from_travel = fields.Date.from_string(
                        record.date_from
                    ) - relativedelta(days=days)
                if record.date_to:
                    record.date_to_travel = fields.Date.from_string(
                        record.date_to
                    ) + relativedelta(days=days)

    @api.depends("date_from", "date_to", "type", "request_type_id")
    def _compute_duration(self):
        for deputation in self:
            duration_imp = duration = 0
            if deputation.date_from and deputation.date_to:
                date_from = fields.Date.from_string(deputation.date_from)
                date_to = fields.Date.from_string(deputation.date_to)
                duration = (date_to - date_from).days + 1
            if deputation.request_type_id:
                duration_imp = 0
                if deputation.type == "internal":
                    if deputation.request_type_id.before_mission_days_internal:
                        duration_imp = (
                            duration_imp
                            + deputation.request_type_id.before_mission_days_internal
                            + deputation.request_type_id.after_mission_days_internal
                        )
                if deputation.type == "external":

                    if deputation.request_type_id.before_mission_days_external:
                        duration_imp = (
                            duration_imp
                            + deputation.request_type_id.before_mission_days_external
                            + deputation.request_type_id.after_mission_days_external
                        )

            deputation.duration = duration + duration_imp

    @api.depends("date_from_travel", "date_to_travel")
    def _compute_duration_holiday_days(self):
        for deputation in self:
            deputation.duration_holiday_days = 0
            start_date = deputation.date_from
            hr_deputation_setting = deputation.env["hr.deputation.setting"].search(
                [], limit=1
            )
            if hr_deputation_setting.multiply_deputation_days:
                if deputation.date_from_travel and deputation.date_to_travel:
                    start_date = (
                        (
                            deputation.date_from_travel
                            - timedelta(
                                days=deputation.request_type_id.before_mission_days_internal
                            )
                        )
                        if deputation.type == "internal"
                        else (
                            deputation.date_from_travel
                            - timedelta(
                                days=deputation.request_type_id.before_mission_days_external
                            )
                        )
                    )

                holiday_days = 0
                # Overlapping holiday with deputation
                holidays = deputation.env["hr.public.holiday"].search(
                    [
                        "&",
                        ("state", "=", "done"),
                        "|",
                        "|",
                        "&",
                        ("date_from", ">=", deputation.date_from),
                        ("date_from", "<=", deputation.date_to),
                        "&",
                        ("date_to", ">=", deputation.date_from),
                        ("date_to", "<=", deputation.date_to),
                        "&",
                        "&",
                        ("date_from", "<=", deputation.date_from),
                        ("date_to", ">=", deputation.date_from),
                        "&",
                        ("date_from", "<=", deputation.date_to),
                        ("date_to", ">=", deputation.date_to),
                    ]
                )

                for day in range(deputation.duration):
                    if start_date:
                        day_date = start_date + timedelta(days=day)
                        # compare each day of deputation with weekend days and holidays
                        if day_date.weekday() in [4, 5] or any(
                            holiday.date_from <= day_date <= holiday.date_to
                            for holiday in holidays
                        ):
                            holiday_days += 1
                deputation.duration_holiday_days = holiday_days

    # ------------------------------------------------------------
    # ORM methods
    # ------------------------------------------------------------
    def name_get(self):
        res = super(HrDeputation, self).name_get()
        for request in self:
            res.append((request.id, request.name))
        return res

    @api.model
    def fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        """fields_view_get to remove create and edit and delete from menu deputation."""
        res = super(HrDeputation, self).fields_view_get(
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

    @api.model
    def create(self, vals):
        """Add sequence."""
        deputation = super(HrDeputation, self).create(vals)
        if deputation:
            deputation.name = self.env["ir.sequence"].next_by_code("hr.deputation.seq")
            for attachment in deputation.attachment_ids.filtered(
                lambda attachment: not attachment.res_id
            ):
                attachment.res_id = deputation.id
        return deputation

    def write(self, vals):
        res = super(HrDeputation, self).write(vals)
        for attachment in self.attachment_ids.filtered(
            lambda attachment: not attachment.res_id
        ):
            attachment.res_id = self.id
        return res

    # ------------------------------------------------------------
    # Constraints methods
    # ------------------------------------------------------------
    @api.constrains("date_from", "date_to")
    def _check_dates(self):
        """Check dates."""
        if self.date_from and self.date_to:
            # Date validation
            if self.date_from > self.date_to:
                raise ValidationError(_("Start date must be less than the end date."))
            # Check intersection
            self.check_intersection()

    @api.constrains("duration", "travel_days")
    def _check_duration(self):
        """Check if duration + travel days depassed annual balance."""
        hr_deputation_setting = self.env["hr.deputation.setting"].search([], limit=1)
        if (
            not hr_deputation_setting.balance_deputation_no_specified
            and self.employee_id
            and self.duration
        ):
            if self.employee_id.deputation_balance < (
                self.duration + int(self.travel_days or 0)
            ):
                # todo: Test Error: 'hr.deputation' object has
                #  no attribute 'deputation_balance_override'
                # self.deputation_balance_override = True
                raise ValidationError(
                    _("The annual deputation balance has been exceeded!")
                )

    def check_intersection(self):
        """Verify.

            i .There is an overlap of dates with a deputation
        :return: ValidationError
        """
        search_domain = [("employee_id", "=", self.employee_id.id)]
        self_id = False
        # داخل في التواريخ مع إنتداب
        if isinstance(self.id, int):
            self_id = self.id
        for rec in self.search(
            search_domain + [("id", "!=", self_id), ("state", "!=", "cancel")]
        ):
            if (
                rec.date_from <= self.date_from <= rec.date_to
                or rec.date_from <= self.date_to <= rec.date_to
                or self.date_from <= rec.date_from <= self.date_to
                or self.date_from <= rec.date_to <= self.date_to
            ):
                raise ValidationError(
                    _("There is an overlap of dates with a deputation")
                )

    @api.onchange(
        "duration",
        "deputation_allowance",
        "travel_days",
        "food",
        "hosing",
        "transport",
        "distance",
        "include_ticket_total_amount",
        "ticket_price",
        "kilometer_amount_overland",
    )
    def _onchange_days(self):
        """Compute Amount and total."""
        # to do get deputation allowance with job position
        hr_deputation_setting = self.env["hr.deputation.allowance"].get_allowance(self)
        amount_holidays = amount_normal_days = 0
        days = self.duration + int(self.travel_days or 0)
        work_day = abs(days - self.duration_holiday_days)

        # compute total and amount with distance
        if (
            hr_deputation_setting
            and hr_deputation_setting.deputation_setting_id
            and hr_deputation_setting.deputation_setting_id.deputation_with_kilometer
        ):
            if self.distance:
                if self.kilometer_amount:
                    amount = self.distance * self.kilometer_amount
                else:
                    amount = self.distance * hr_deputation_setting.kilometer_amount
            else:
                if hr_deputation_setting.deputation_setting_id.multiply_deputation_days:
                    # flake8: noqa: B950
                    amount_holidays = abs(
                        self.deputation_allowance
                        * self.duration_holiday_days
                        * hr_deputation_setting.deputation_setting_id.multiply_deputation_holidays_days
                    )
                    amount_normal_days = self.deputation_allowance * work_day

                    amount = abs(self.deputation_allowance * work_day) + (
                        self.deputation_allowance
                        * self.duration_holiday_days
                        * hr_deputation_setting.deputation_setting_id.multiply_deputation_holidays_days
                    )
                else:
                    amount = abs(self.deputation_allowance * days)
        # compute total and amount with duration and travel_days
        else:
            if hr_deputation_setting.deputation_setting_id.multiply_deputation_days:
                amount_holidays = (
                    self.deputation_allowance
                    * self.duration_holiday_days
                    * hr_deputation_setting.deputation_setting_id.multiply_deputation_holidays_days
                )
                amount_normal_days = self.deputation_allowance * work_day

                amount = (self.deputation_allowance * work_day) + (
                    self.deputation_allowance
                    * self.duration_holiday_days
                    * hr_deputation_setting.deputation_setting_id.multiply_deputation_holidays_days
                )
            else:
                amount = self.deputation_allowance * days

        self.total = amount
        self.amount_holidays = amount_holidays
        self.amount_normal_days = amount_normal_days

        # add ticket amount to total price
        if self.include_ticket_total_amount:
            self.total += self.ticket_price
        if self.distance and self.ticket_price:
            self.total += self.ticket_price
        if self.kilometer_amount_overland:
            self.total += self.kilometer_amount_overland

    @api.onchange("type", "distance", "transport", "food", "hosing")
    def _onchange_type(self):
        # calcul deputation allowance
        food = transport = hosing = 0
        if self.type:
            if self.type == "internal":
                self.location_ids = [(6, 0, [])]
            if self.type == "external":
                self.country_id = False
                self.city_id = False
        deputation_allowance_obj = self.env["hr.deputation.allowance"]
        # get deputation allowance with job position
        hr_deputation_setting = deputation_allowance_obj.get_allowance(self)
        if (
            hr_deputation_setting
            and hr_deputation_setting.deputation_setting_id
            and hr_deputation_setting.deputation_setting_id.deputation_with_kilometer
        ):
            if self.distance:
                if self.kilometer_amount:
                    self.deputation_allowance = self.distance * self.kilometer_amount
                else:
                    self.deputation_allowance = (
                        self.distance * hr_deputation_setting.kilometer_amount
                    )
            else:
                if self.type:
                    # get deputation_allowance value from setting
                    (
                        deputation_allowance,
                        transport_amount,
                    ) = deputation_allowance_obj.get_deputation_allowance_amount(
                        self.type, self
                    )
                    self.deputation_allowance = deputation_allowance
        else:
            if self.type:
                # get deputation_allowance value from setting
                (
                    deputation_allowance,
                    transport_amount,
                ) = deputation_allowance_obj.get_deputation_allowance_amount(
                    self.type, self
                )
                self.deputation_allowance = deputation_allowance
                # remove food amount of from deputation_allowance
        if self.food:
            food = self.deputation_allowance / 100 * hr_deputation_setting.food
            # remove transport amount of from deputation_allowance
        if self.transport:
            transport = (
                self.deputation_allowance / 100 * hr_deputation_setting.transport
            )
            # remove hosing amount of from deputation_allowance
        if self.hosing:
            hosing = self.deputation_allowance / 100 * hr_deputation_setting.hosing
        self.deputation_allowance -= food + transport + hosing

    # ------------------------------------------------------------
    # Onchange methods
    # ------------------------------------------------------------
    @api.onchange("transportation_type")
    def _onchange_transportation_type(self):
        if self.transportation_type == "overland":
            self.include_ticket_total_amount = self.ticket_price = False
        if self.transportation_type == "air_travel":
            self.distance = self.ticket_price = 0

    @api.onchange("employee_id")
    def _onchange_employee_id(self):
        if self.employee_id:
            self.job_id = (
                self.employee_id.job_id.id if self.employee_id.job_id else False
            )
            self.department_id = (
                self.employee_id.department_id.id
                if self.employee_id.department_id
                else False
            )
            # get deputation_allowance value from setting
            deputation_allowance_obj = self.env["hr.deputation.allowance"]
            (
                deputation_amount,
                deputation_transport,
            ) = deputation_allowance_obj.get_deputation_allowance_amount(
                self.type, self
            )
            self.deputation_allowance = deputation_amount
            self.ticket_type = deputation_allowance_obj._get_ticket_type(self)

    @api.onchange("country_id", "location_ids", "city_id")
    def onchange_country_id(self):
        """Calculate travel days from deputation settings."""
        deputation_allowance_obj = self.env["hr.deputation.allowance"]
        # take travel days for first location
        if self.location_ids and self.employee_id:
            self.travel_days = deputation_allowance_obj.get_travel_days(
                self.location_ids[0].country_id, self
            )
        # country by default SA
        elif self.country_id and self.employee_id:
            self.travel_days = deputation_allowance_obj.get_travel_days(
                self.country_id, self
            )
        # nothing to do it
        else:
            pass

    @api.onchange("request_type_id", "duration")
    def _onchange_request_type(self):
        super(HrDeputation, self)._onchange_request_type()
        if self.request_type_id:
            self.need_fees = self.request_type_id.need_fees

    # ------------------------------------------------------------
    # Business methods
    # ------------------------------------------------------------
    def action_send(self):
        """Send the request to be approved by the right users."""
        for deputation in self:
            if not deputation.read_reviewed_policies_regulations:
                raise ValidationError(
                    _("You must read and reviewed the policies regulations")
                )
            super(HrDeputation, self).action_send()

    def update_deputation_stock(self):
        """Update stock of employees every worked year."""
        employees = self.env["hr.employee"].search([])
        today_date = fields.Date.from_string(fields.Date.today())
        deputation_setting = self.env["hr.deputation.setting"].search([], limit=1)
        # Update stock of deputation for employee every year
        for employee in employees:
            stock_line = self.env["hr.employee.deputation.stock"].search(
                [("employee_id", "=", employee.id)]
            )
            if (
                deputation_setting
                and deputation_setting.annual_balance > 0
                and stock_line
            ):
                deputation_available_stock = deputation_setting.annual_balance
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
                            "deputation_available_stock": stock_line.deputation_available_stock
                            + deputation_available_stock
                            if deputation_setting.accumulative_balance
                            else deputation_available_stock,
                            "current_stock": deputation_available_stock,
                            "token_deputation_sum": 0,
                        }
                    )

    @api.model
    def initialize_deputation_stock(self):
        """Initialize deputation stock."""
        dep_setting = self.env["hr.deputation.setting"].search([], limit=1)
        obj_deputation_stock = self.env["hr.employee.deputation.stock"]
        for employee in self.env["hr.employee"].search([]):
            deputation_stock = obj_deputation_stock.search(
                [("employee_id", "=", employee.id)]
            )
            if dep_setting and dep_setting.annual_balance > 0 and not deputation_stock:
                deputation_available_stock = dep_setting.annual_balance
                deputation_stock.sudo().create(
                    {
                        "deputation_available_stock": deputation_available_stock,
                        "current_stock": deputation_available_stock,
                        "employee_id": employee.id,
                    }
                )

    def button_cancel(self):
        """Cancel deputation.

        :return: Dictionary: Form view
        """
        self.ensure_one()
        view_id = self.env.ref("hr_deputation.hr_deputation_cancellation_view_form").id
        context = self._context.copy()
        context.update(
            {
                "default_deputation_id": self.id,
                "default_employee_id": self.employee_id.id,
                "default_company_id": self.company_id.id,
                "default_date_from": self.date_from,
                "default_date_to": self.date_to,
                "default_duration": self.duration,
            }
        )
        return {
            "name": "Deputation Cancel",
            "view_type": "form",
            "view_mode": "tree",
            "views": [(view_id, "form")],
            "res_model": "hr.deputation.cancellation",
            "view_id": view_id,
            "type": "ir.actions.act_window",
            "res_id": False,
            "target": "current",
            "context": context,
        }

    def button_cut(self):
        """Create a cut deputation object.

        :return: Dictionary: form view
        """
        self.ensure_one()
        view_id = self.env.ref("hr_deputation.hr_deputation_cut_view_form").id
        context = self._context.copy()
        context.update(
            {
                "default_deputation_id": self.id,
                "default_employee_id": self.employee_id.id,
                "default_company_id": self.company_id.id,
                "default_date_from": self.date_from,
                "default_date_to": self.date_to,
                "default_duration": self.duration,
            }
        )
        return {
            "name": "Deputation Cut",
            "view_type": "form",
            "view_mode": "tree",
            "views": [(view_id, "form")],
            "res_model": "hr.deputation.cut",
            "view_id": view_id,
            "type": "ir.actions.act_window",
            "res_id": False,
            "target": "current",
            "context": context,
        }

    def button_extend(self):
        """Extend deputation.

        :return: Dictionary: Form view
        """
        view_id = self.env.ref("hr_deputation.hr_deputation_extension_view_form").id
        context = self._context.copy()
        context.update(
            {
                "default_deputation_id": self.id,
                "default_employee_id": self.employee_id.id,
                "default_company_id": self.company_id.id,
                "default_date_from": self.date_from,
                "default_date_to": self.date_to,
                "default_duration": self.duration,
            }
        )
        return {
            "name": "Extension Deputation",
            "view_type": "form",
            "view_mode": "tree",
            "views": [(view_id, "form")],
            "res_model": "hr.deputation.extension",
            "view_id": view_id,
            "type": "ir.actions.act_window",
            "res_id": False,
            "target": "current",
            "context": context,
        }

    def action_accept(self):
        """Accept the request and Send it to be approved by the right users."""
        for rec in self:
            super(HrDeputation, rec).action_accept()
            if rec.state == "done":
                stock_line = (
                    self.env["hr.employee.deputation.stock"]
                    .sudo()
                    .search([("employee_id", "=", rec.employee_id.id)], limit=1)
                )
                if stock_line:
                    stock_line.sudo().token_deputation_sum += rec.duration + int(
                        rec.travel_days or 0
                    )
        return True

    def action_cancel(self):
        for deputation in self:
            if deputation.state == "done":
                stock_line = deputation.env["hr.employee.deputation.stock"].search(
                    [("employee_id", "=", deputation.employee_id.id)], limit=1
                )
                if stock_line:
                    stock_line.token_deputation_sum -= deputation.duration + int(
                        deputation.travel_days or 0
                    )
            deputation.stage_id = deputation._get_next_stage(stage_type="cancel")
            deputation._onchange_stage_id()
            deputation._make_done_activity()
            deputation.canceled = True

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

                if stage_obj and stage_obj.appears_in_deputation_report:
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

    # ------------------------------------------------------------
    # Override methods
    # ------------------------------------------------------------

    def _sync_employee_details(self):
        for deputation in self:
            super(HrDeputation, deputation)._sync_employee_details()
            if deputation.employee_id:
                deputation.number = deputation.employee_id.number
                deputation.company_id = deputation.company_id.id


class RequestType(models.Model):
    _inherit = "request.type"

    before_mission_days_internal = fields.Integer(
        string="Number of days before an internal mission"
    )
    after_mission_days_internal = fields.Integer(
        string="Number of days after an internal mission"
    )
    before_mission_days_external = fields.Integer(
        string="Number of days before an external mission"
    )
    after_mission_days_external = fields.Integer(
        string="Number of days after an external mission"
    )
    need_fees = fields.Boolean(string="Need Fees", default=False)


class HrDeputationLocation(models.Model):
    _name = "hr.deputation.location"
    _description = "Deputation Location"

    deputation_id = fields.Many2one(
        "hr.deputation", string="Deputation", ondelete="cascade"
    )
    country_id = fields.Many2one(
        "res.country", string="Country", domain=[("code", "!=", "SA")], required=1
    )
    city_name = fields.Char(string="City")
