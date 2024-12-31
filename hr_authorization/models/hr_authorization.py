from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HrAuthorization(models.Model):
    _name = "hr.authorization"
    _description = "Authorization"
    _inherit = ["request"]

    active = fields.Boolean(default=True)
    hour_start = fields.Float(
        string="Exit hour", readonly=1, states={"draft": [("readonly", 0)]}
    )
    hour_stop = fields.Float(
        string="Return hour", readonly=1, states={"draft": [("readonly", 0)]}
    )
    duration = fields.Float(string="Duration", readonly=1)
    description = fields.Text(
        string="Description", readonly=1, states={"draft": [("readonly", 0)]}
    )
    current_authorization_hours = fields.Float(
        string="Current Authorization stock",
        compute="_compute_authorization_stock",
        store=1,
    )
    current_nb_authorization = fields.Integer(
        string="Number of authorization",
        compute="_compute_authorization_stock",
        store=1,
    )
    canceled = fields.Boolean(default=False, copy=False)
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
        readonly=1,
        states={"draft": [("readonly", 0)]},
    )
    attachment_ids = fields.Many2many(
        "ir.attachment",
        string="Attachments",
        readonly=1,
        states={"draft": [("readonly", 0)]},
    )

    @api.model
    def _get_domain(self):
        domain = False
        current_employee = self.env["hr.employee"].search(
            [("user_id", "=", self._uid)], limit=1
        )

        # Set default domain to current employee
        if current_employee:
            domain = [("id", "=", current_employee.id)]

        # Get employees of current user
        employee_ids = self.env["hr.employee"].search(
            [("parent_id.user_id", "=", self.env.user.id)]
        )
        employee_ids = employee_ids.ids

        # Add current employee to employee_ids
        if current_employee:
            employee_ids.append(current_employee.id)

        # Manager can see all employees : no constraint
        if self.env.user.has_group("hr_authorization.group_hr_authorization_manager"):
            domain = []
        # Officer(user) can see only his employees
        elif self.env.user.has_group("hr_authorization.group_hr_authorization_user"):
            domain = [("id", "in", employee_ids)]
        return domain

    employee_id = fields.Many2one(domain=_get_domain)

    # ------------------------------------------------------------
    # Compute methods
    # ------------------------------------------------------------

    @api.depends("stage_id")
    def _compute_display_button(self):
        for rec in self:
            super(HrAuthorization, rec)._compute_display_button()
            rec.display_button_send = False
            if rec.state == "draft":
                if (
                    (
                        rec.employee_id.user_id
                        and rec.employee_id.user_id.id == rec.env.user.id
                    )
                    or (
                        rec.employee_id.parent_id
                        and rec.employee_id.parent_id.user_id.id == rec.env.user.id
                    )
                    or rec.env.user.has_group(
                        "hr_authorization.group_hr_authorization_manager"
                    )
                ):
                    rec.display_button_send = True

    # ------------------------------------------------------------
    # Onchange methods
    # ------------------------------------------------------------
    @api.onchange("hour_start", "hour_stop")
    def _onchange_duration(self):
        self.duration = (self.hour_stop) - (self.hour_start)

    def _sync_employee_details(self):
        for authorization in self:
            super(HrAuthorization, authorization)._sync_employee_details()
            if authorization.employee_id:
                authorization.company_id = authorization.company_id.id

    # ------------------------------------------------------------
    # ORM methods
    # ------------------------------------------------------------
    @api.model
    def create(self, values):
        authorization = super(HrAuthorization, self).create(values)
        authorization.attachment_ids.filtered(
            lambda attachment: not attachment.res_id
        ).write({"res_id": authorization.id})
        authorization.name = self.env["ir.sequence"].next_by_code(
            "hr.authorization.seq"
        )
        return authorization

    def write(self, vals):
        authorization = super(HrAuthorization, self).write(vals)
        self.attachment_ids.filtered(lambda attachment: not attachment.res_id).write(
            {"res_id": self.id}
        )
        return authorization

    # ------------------------------------------------------------
    # Constraints methods
    # ------------------------------------------------------------
    @api.constrains("hour_start", "hour_stop")
    def _check_duration(self):
        if self.hour_start > self.hour_stop:
            raise ValidationError(_("Return hour should be greater than exit hour."))
        self.check_intersection()

    @api.constrains("request_type_id")
    def _check_required_attachments(self):
        """check if required attachments equal to True"""
        for authorization in self:
            if (
                authorization.request_type_id.required_attachments
                and not authorization.attachment_ids
            ):
                raise ValidationError(_("You have to insert your attachments first"))

    def check_intersection(self):
        """Check intersection with authorization."""
        # intersection in dates with another authorization
        for rec in self.search(
            [
                ("employee_id", "=", self.employee_id.id),
                ("state", "=", "done"),
                ("date", "=", self.date),
            ]
        ):
            if (
                rec.hour_start <= self.hour_start <= rec.hour_stop
                or rec.hour_start <= self.hour_stop <= rec.hour_stop
                or self.hour_start <= rec.hour_start <= self.hour_stop
                or self.hour_start <= rec.hour_stop <= self.hour_stop
            ):
                raise ValidationError(
                    _("There's an intersection in dates with another authorization")
                )

    @api.depends(
        "employee_id", "request_type_id", "hour_start", "hour_stop", "date", "state"
    )
    def _compute_authorization_stock(self):
        authorization_obj = self.env["hr.authorization"]
        for rec in self:
            current_authorization_hours = 0
            current_nb_authorization = 0
            month = rec.date.month
            year = rec.date.year
            if rec.employee_id and rec.request_type_id:
                taken_auth_current_month = authorization_obj.search(
                    [
                        ("employee_id", "=", rec.employee_id.id),
                        ("request_type_id", "=", rec.request_type_id.id),
                        ("state", "!=", "cancel"),
                    ]
                )
                current_authorization_hours = rec.request_type_id.hours_authorization
                taken_auth_current_month = taken_auth_current_month.filtered(
                    lambda auth: auth.date.month == month and auth.date.year == year
                )
                if taken_auth_current_month:
                    taken_authorization = sum(
                        authorization.duration
                        for authorization in taken_auth_current_month
                    )
                    current_authorization_hours = (
                        current_authorization_hours - taken_authorization
                    )
                    current_nb_authorization = len(taken_auth_current_month)
            rec.current_authorization_hours = current_authorization_hours
            rec.current_nb_authorization = current_nb_authorization

    @api.constrains("request_type_id", "hour_start", "hour_stop", "date")
    def _check_hours(self):
        for rec in self:
            if rec.date and rec.request_type_id:
                if (
                    rec.current_nb_authorization
                    and rec.request_type_id.number_authorization
                    < rec.current_nb_authorization
                ):
                    raise ValidationError(
                        _("You have met the allowed number of authorization per month")
                    )
                if (
                    rec.current_authorization_hours
                    and rec.current_authorization_hours < 0
                    and rec.request_type_id.hours_authorization
                ):
                    raise ValidationError(
                        _("You do not have sufficient hours of authorization")
                    )

    def action_cancel(self):
        for authorization in self:
            authorization.stage_id = authorization._get_next_stage(stage_type="cancel")
            authorization._onchange_stage_id()
            authorization._make_done_activity()
            authorization.canceled = True


class HrAuthorizationType(models.Model):
    _inherit = "request.type"
    _description = "HR Authorization Type"

    hours_authorization = fields.Float(string="Number of authorization hours")
    number_authorization = fields.Integer(string="Number of authorizations")
    required_attachments = fields.Boolean(string="Required Attachments")
