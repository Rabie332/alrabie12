from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.osv import expression
from odoo.tools.safe_eval import safe_eval


class Request(models.AbstractModel):
    _name = "request"
    _description = "Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "id desc"
    _group_by_full = {"stage_id": lambda s, *a, **k: s._read_group_stage_ids(*a, **k)}

    @api.model
    def _default_employee_id(self):
        employees = self.env["hr.employee"].search(
            [("user_id", "=", self._uid)], limit=1
        )
        return employees and employees[0]

    #   _default_stage_id was added because onchange of 'branch'
    #   was triggering the default value of stage_id.
    @api.model
    def _default_stage_id(self):
        return self._get_next_stage(stage_type="default")

    name = fields.Char(string="Number", readonly=1)
    stage_id = fields.Many2one(
        "request.stage",
        string="Stage",
        tracking=True,
        index=True,
        copy=False,
        domain=lambda self: ""
        "[('res_model_id.model', '=', '" + self._name + "'), ('state', '!=', 'cancel'),"
        "'|', ('request_type_ids', '=', False), ('request_type_ids', '=', request_type_id)]",
        group_expand="_read_group_stage_ids",
        default=_default_stage_id,
    )
    employee_id = fields.Many2one(
        "hr.employee",
        string="Employee",
        index=True,
        default=_default_employee_id,
        tracking=True,
        readonly=1,
        states={"draft": [("readonly", 0)]},
    )
    department_id = fields.Many2one("hr.department", string="Department", readonly=1)
    job_id = fields.Many2one("hr.job", string="Job", readonly=1)
    manager_id = fields.Many2one("hr.employee", string="Manager", readonly=True)
    kanban_color = fields.Integer(string="Kanban Color Index")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("in_progress", "In progress"),
            ("cancel", "Cancel"),
            ("done", "Done"),
        ],
        copy=False,
        default="draft",
        string="State",
    )
    date = fields.Date(string="Request date", default=fields.Date.today, readonly=1)
    display_button_refuse = fields.Boolean(
        compute="_compute_display_button", string="Display Button Refuse"
    )
    display_button_send = fields.Boolean(
        compute="_compute_display_button", string="Display Button Send"
    )
    display_button_accept = fields.Boolean(
        compute="_compute_display_button", string="Display Button Accept"
    )
    display_button_previous = fields.Boolean(
        compute="_compute_display_button", string="Display Button Previous"
    )
    request_type_id = fields.Many2one(
        "request.type",
        string="Type",
        domain=lambda self: [("res_model", "=", self._name)],
        readonly=1,
        states={"draft": [("readonly", 0)]},
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        readonly=1,
        states={"draft": [("readonly", 0)]},
    )
    active = fields.Boolean(default=True, string="Active")

    # ------------------------------------------------------------
    # Onchange methods
    # ------------------------------------------------------------
    @api.onchange("request_type_id")
    def _onchange_request_type(self):
        self.stage_id = self._get_next_stage(stage_type="default")
        self._onchange_stage_id()

    @api.onchange("employee_id")
    def _onchange_employee_id(self):
        self._sync_employee_details()

    def _sync_employee_details(self):
        for request in self:
            if request.employee_id:
                request.manager_id = request.employee_id.parent_id
                request.department_id = request.employee_id.department_id
                request.job_id = request.employee_id.job_id
                request.company_id = request.employee_id.company_id

    @api.onchange("stage_id")
    def _onchange_stage_id(self):
        if self.stage_id and self.stage_id.state:
            self.state = self.stage_id.state

    def add_follower(self, employee_id):
        employee = self.env["hr.employee"].browse(employee_id)
        if employee.user_id:
            self.message_subscribe(partner_ids=employee.user_id.partner_id.ids)

    # ------------------------------------------------------------
    # ORM Overrides methods
    # ------------------------------------------------------------

    @api.model
    def create(self, values):
        """Call sync_employee_details."""
        employee_id = values.get("employee_id", False)
        request = super(Request, self).create(values)
        request.add_follower(employee_id)
        if "employee_id" in values:
            request._sync_employee_details()
        return request

    def write(self, values):
        """Call sync_employee_details."""
        employee_id = values.get("employee_id", False)
        request = super(Request, self).write(values)
        self.add_follower(employee_id)
        if "employee_id" in values:
            self._sync_employee_details()
        return request

    def unlink(self):
        """Delete request only if state draft or cancel."""
        for request in self.filtered(lambda request: request.state not in ["draft"]):
            raise UserError(
                (_("You cannot delete a request which is in {0} stage.")).format(
                    request.stage_id.name
                )
            )
        return super(Request, self).unlink()

    @api.returns("self", lambda value: value.id)
    def copy(self, default=None):
        default = default or {}
        default.update({"state": "draft"})
        return super(Request, self).copy(default)

    def name_get(self):
        res = []
        for request in self:
            res.append(
                (
                    request.id,
                    _("%s have an %s request on : %s ")
                    % (request.employee_id.name, self._description, request.date),
                )
            )
        return res

    # ------------------------------------------------------------
    # Compute methods
    # ------------------------------------------------------------
    @api.depends("stage_id")
    def _compute_display_button(self):
        # todo: manager can create request for another employee  and send it to dm
        for rec in self:
            users = rec._get_approvers()
            rec.display_button_refuse = False
            rec.display_button_accept = False
            rec.display_button_send = False
            rec.display_button_previous = False
            if (
                rec.state == "draft"
                and rec.employee_id.user_id
                and rec.employee_id.user_id.id == rec.env.uid
            ):
                rec.display_button_send = True
            elif rec.state == "in_progress" and rec.env.uid in users:
                rec.display_button_accept = True
                rec.display_button_refuse = True
                rec.display_button_previous = True

    # ------------------------------------------------------------
    # Activity methods
    # ------------------------------------------------------------
    def _get_approvers(self):
        users = []
        # Notify users to approve or return feedback
        if self.stage_id.assign_type == "user":
            if self.stage_id.sudo().default_user_id:
                users.append(self.stage_id.sudo().default_user_id.id)
        else:
            if self.stage_id.assign_type == "role":
                for role in self.stage_id.sudo().default_role_ids:
                    for user in role.sudo().user_ids:
                        users.append(user.id)
            if self.stage_id.assign_type == "python":
                try:
                    eval_dict = {"object": self.sudo(), "env": self.env, "result": None}
                    code = self.stage_id.code.strip()
                    safe_eval(code, eval_dict, mode="exec", nocopy=True)
                    # the result of the evaluated code is put in the 'result' local variable
                    # propagated to the context
                    result = eval_dict.get("result")
                    if (
                        result is not None
                        and isinstance(result, (object))
                        and result._name == "res.users"
                    ):
                        if len(result) == 1:
                            users.append(result.sudo().id)
                        else:
                            for user in result:
                                users.append(user.id)
                except Exception:
                    pass
            if users:
                users = [user.id for user in self.env["res.users"].sudo().browse(users)]
        return users

    def action_feedback(self):
        """Return the feedback and marke done all activities."""
        self._make_done_activity()
        model_name = self._name.replace(".", "_")
        name = self._get_ir_model_data_name("mail_{}_".format(model_name) + "feedback")
        if name:
            for user in self._get_approvers():
                self.activity_schedule(name, user_id=user)
        return True

    def _get_ir_model_data_name(self, name):
        res_name = False
        model_data = (
            self.env["ir.model.data"].sudo().search([("name", "=", name)], limit=1)
        )
        if model_data:
            res_name = "{}.{}".format(model_data.module, name)
        return res_name

    def _action_schedule_activity(self, user):
        """Schedule activity for specific user."""
        model_name = self._name.replace(".", "_")
        name = self._get_ir_model_data_name("mail_{}_".format(model_name) + "approval")
        if name:
            self.activity_schedule(name, user_id=user)

    def activity_update(self):
        """Schedule the next activity."""
        self._make_done_activity()
        if self.state in ("draft", "in_progress"):
            for user in self._get_approvers():
                self._action_schedule_activity(user)
        return True

    def _make_done_activity(self):
        """Make done all activities of type validation."""
        activitys = self.env["mail.activity"].search(
            [
                ("activity_type_id.category", "=", "validation"),
                ("res_model", "=", self._name),
                ("res_id", "=", self.id),
            ]
        )
        for activity in activitys:
            activity.active = False

    def get_approvals_details(self, field="stage_id"):
        # filter messages per stage
        for request in self:
            track_obj = request.env["mail.tracking.value"]
            ir_model = self.env["ir.model"].search([("model", "=", request._name)])
            ir_model_field = request.env["ir.model.fields"].search(
                [("model_id", "=", ir_model.id), ("name", "=", field)]
            )
            tracking_lines = track_obj.sudo().search(
                [
                    ("mail_message_id.res_id", "=", request.id),
                    ("mail_message_id.model", "=", request._name),
                    ("field", "=", ir_model_field.id),
                    ("old_value_char", "!=", ""),
                ]
            )
            values = {}
            for track in tracking_lines:
                stage = request.env["request.stage"].browse(track.old_value_integer)
                if stage and stage.state != "cancel":
                    values.update(
                        {
                            track.old_value_char: {
                                "date": track.mail_message_id.date,
                                "approver": track.create_uid,
                                "stage_id": track.old_value_integer,
                            }
                        }
                    )
                else:
                    values.update(
                        {
                            track.new_value_char: {
                                "date": track.mail_message_id.date,
                                "approver": track.create_uid,
                                "stage_id": track.new_value_integer,
                            }
                        }
                    )
            return values

    # ------------------------------------------------------------
    # Business methods
    # ------------------------------------------------------------
    def _read_group_stage_ids(self, stages, domain, order):
        search_domain = [("res_model_id.model", "=", self._name)]
        search_domain = expression.AND([search_domain, self._get_extra_domain()])
        return stages.search(search_domain, order=order)

    def _get_extra_domain(self):
        search_domain = []
        # append the domain of type to general domain
        if self.request_type_id:
            search_domain = expression.AND(
                [
                    search_domain,
                    [
                        "|",
                        ("request_type_ids", "=", False),
                        ("request_type_ids", "in", [self.request_type_id.id]),
                    ],
                ]
            )
        else:
            search_domain = expression.AND(
                [search_domain, [("request_type_ids", "=", False)]]
            )
        return search_domain

    def _get_next_stage(self, stage_type="next"):
        """Return the next stage with specified the model state and next sequence."""
        # declared general domain it will be used for all requests
        search_domain = [("res_model", "=", self._name)]
        if stage_type == "default":
            search_domain = expression.AND([search_domain, [("state", "=", "draft")]])
        elif stage_type == "cancel":
            search_domain = expression.AND([search_domain, [("state", "=", "cancel")]])
        else:

            search_domain = expression.AND(
                [
                    search_domain,
                    [
                        ("state", "not in", ["cancel", "draft"]),
                        ("sequence", ">", self.stage_id.sequence),
                    ],
                ]
            )
        search_domain = expression.AND([search_domain, self._get_extra_domain()])
        next_stage = self.env["request.stage"].search(
            search_domain, order="sequence asc", limit=1
        )
        return next_stage

    def action_send(self):
        """Send the request to be approved by the right users."""
        for request in self:
            if request.stage_id and request.state == "draft":
                request.stage_id = request._get_next_stage()
                request._onchange_stage_id()
                request.activity_update()

    def action_accept(self):
        """Accept the request and Send it to be approved by the right users."""
        for request in self:
            if request.stage_id and request.state == "in_progress":
                request.stage_id = request._get_next_stage()
                request._onchange_stage_id()
                # Schedule the next activity
                if request.state != "done":
                    request.activity_update()
                # Send feedback to users
                else:
                    request.action_feedback()
            return True

    def action_refuse(self):
        """Refuse the request and return feedback to users."""
        for request in self:
            if request.stage_id and request.state == "in_progress":
                request.stage_id = request._get_next_stage(stage_type="cancel")
                request._onchange_stage_id()
                request.action_feedback()
            return True

    def open_multi_refuse_wizard(self):
        return {
            "name": _("Warning"),
            "res_model": "confirm.action.wizard",
            "view_mode": "form",
            "context": {
                "active_model": self._name,
                "active_ids": self.ids,
                "refuse": True,
            },
            "target": "new",
            "type": "ir.actions.act_window",
        }

    def open_multi_accept_wizard(self):
        return {
            "name": _("Warning"),
            "res_model": "confirm.action.wizard",
            "view_mode": "form",
            "context": {
                "active_model": self._name,
                "active_ids": self.ids,
                "accept": True,
            },
            "target": "new",
            "type": "ir.actions.act_window",
        }

    def _get_previous_stage(self):
        """Return the previous stage with specified the model state and next sequence."""
        # declared general domain it will be used for all requests
        search_domain = [
            ("res_model", "=", self._name),
            ("state", "in", ["draft", "in_progress"]),
            ("sequence", "<", self.stage_id.sequence),
        ]
        search_domain = expression.AND([search_domain, self._get_extra_domain()])
        previous_stage = self.env["request.stage"].search(
            search_domain, order="sequence desc", limit=1
        )
        return previous_stage

    def action_previous_stage(self):
        """Return the request to the previous stage."""
        for request in self:
            if request.stage_id and request.state == "in_progress":
                request.stage_id = request._get_previous_stage()
                request._onchange_stage_id()
                request.activity_update()

    # ------------------------------------------------------------
    # Messaging methods
    # ------------------------------------------------------------
    def _track_subtype(self, init_values):
        """Give the subtypes triggered by the changes on the record according
        to values that have been updated.

        :param init_values: the original values of the record; only modified fields
                            are present in the dict

        each module inherit  from request should define two mail.message.subtype :
        1- ('%s.mt_%s_approved') % (module_name, model_name),
            example hr_authorization.mt_hr_authorization_approved
        2- ('%s.mt_%s_refused') % (module_name, model_name),
            example hr_authorization.mt_hr_authorization_refused
        """
        if "stage_id" in init_values and self.stage_id.state in ("done", "cancel"):
            model_name = self._name.replace(".", "_")
            if self.stage_id.state == "done":
                name = self._get_ir_model_data_name(
                    "mt_{}_".format(model_name) + "approved"
                )
            elif self.stage_id.state == "cancel":
                name = self._get_ir_model_data_name(
                    "mt_{}_".format(model_name) + "refused"
                )
            if name:
                return self.env.ref(name)
        return super(Request, self)._track_subtype(init_values)


class RequestType(models.Model):
    _name = "request.type"
    _description = " Request Type"

    @api.model
    def _default_res_model_id(self):
        """Use when creating type from a tree view for another model."""
        if self.env.context.get("default_res_model"):
            return self.env["ir.model"]._get(self.env.context.get("default_res_model"))

    code = fields.Char(string="Code")
    name = fields.Char(string="Name", required=1, translate=True)
    res_model_id = fields.Many2one(
        "ir.model",
        required=True,
        index=True,
        string="Associated Model",
        domain=[("transient", "=", False)],
        default=_default_res_model_id,
        ondelete="cascade",
    )
    res_model = fields.Char("Related Document Model")
    active = fields.Boolean(default=True)
