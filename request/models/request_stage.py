from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import datetime, test_python_expr


class RequestStage(models.Model):
    _name = "request.stage"
    _description = "Stage"
    _order = "sequence"

    DEFAULT_PYTHON_CODE = """
# Available variables:
#  - env: Odoo Environment
#  - object: object is the current object
#  - Example :
# result = object.employee_id.user_id
# or
# result = env['res.users'].search([('id', '=', object.employee_id.user_id.id)])
# \n\n\n\n
"""

    @api.model
    def _default_res_model_id(self):
        """Use when creating stages from a Kanban view for another model."""
        if self.env.context.get("default_res_model"):
            return self.env["ir.model"]._get(self.env.context.get("default_res_model"))

    name = fields.Char(string="Stage Name", required=True, translate=True)
    name_dept = fields.Char(string="Stage Department", translate=True)
    description = fields.Text(string="Description", translate=True)
    sequence = fields.Integer(string="Sequence", default=1)
    mail_template_id = fields.Many2one("mail.template", string="Email Template")
    fold = fields.Boolean(string="Folded in Kanban")
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
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("in_progress", "In progress"),
            ("cancel", "Cancel"),
            ("done", "Done"),
        ],
        copy=False,
        string="State",
    )
    assign_type = fields.Selection(
        [("user", "User"), ("role", "Role"), ("python", "Python Expression")],
        default="user",
        string="Assign Type",
    )
    default_role_ids = fields.Many2many("res.users.role", string="Default roles")
    default_user_id = fields.Many2one("res.users", string="Default user")
    code = fields.Text("Python Code", default=DEFAULT_PYTHON_CODE)
    request_type_ids = fields.Many2many("request.type", string="Types", copy=False)
    active = fields.Boolean(string="Active", default=True)
    move_next_stage = fields.Boolean("Allow automatic transition to the next stage")
    days_number = fields.Integer("The number of waiting days")

    # ------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------
    def request_next_stage(self):
        for stage in self.env["request.stage"].search([("move_next_stage", "=", True)]):
            requests = stage.env[stage.res_model].search([("stage_id", "=", stage.id)])
            for request in requests:
                stages_details = request.sudo().get_approvals_details()
                if stages_details:
                    date_last_approve = (
                        list(stages_details.values())[-1].get("date")
                    ).date()
                    if (
                        date_last_approve
                        and date_last_approve + relativedelta(days=+stage.days_number)
                        < datetime.datetime.now().date()
                    ):
                        request.stage_id = request._get_next_stage()
                        request._onchange_stage_id()
                        request.activity_update()

    # ------------------------------------------------------------
    # Constraints methods
    # ------------------------------------------------------------

    @api.constrains("code")
    def _check_python_code(self):
        for action in self.sudo().filtered("code"):
            msg = test_python_expr(expr=action.code.strip(), mode="exec")
            if msg:
                raise ValidationError(msg)
