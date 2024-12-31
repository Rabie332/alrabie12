from lxml import etree

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HrCovenant(models.Model):
    _name = "hr.covenant"
    _inherit = ["request"]
    _description = "Covenant"
    _rec_name = "name"
    _order = "date"

    covenant_type_id = fields.Many2one(
        "hr.covenant.type",
        string="Covenant Type",
        required=1,
        readonly=1,
        states={"draft": [("readonly", 0)]},
    )
    active = fields.Boolean(default=True)
    employee_id = fields.Many2one(
        "hr.employee",
        string="Employee",
        required=1,
        readonly=1,
        states={"draft": [("readonly", 0)]},
        default=False,
    )
    description = fields.Text(
        "Description", readonly=1, states={"draft": [("readonly", 0)]}
    )
    received_date = fields.Date(
        "Received Date",
        readonly=0,
        states={"done": [("readonly", 1)]},
    )
    number = fields.Char(string="Job number", readonly=1)
    name = fields.Char(required=1, readonly=1, states={"draft": [("readonly", 0)]})
    retrieval = fields.Boolean(default=False, copy=False)
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

    def action_retrieval(self):
        for rec in self:
            rec.retrieval = True

    def _sync_employee_details(self):
        super(HrCovenant, self)._sync_employee_details()
        for request in self:
            if request.employee_id:
                request.number = request.employee_id.number

    @api.model
    def create(self, vals):
        """Add sequence."""
        covenant = super(HrCovenant, self).create(vals)
        if covenant:
            for attachment in covenant.attachment_ids.filtered(
                lambda attachment: not attachment.res_id
            ):
                attachment.res_id = covenant.id
        stage_id = (
            self.env["request.stage"]
            .search(
                [("res_model_id.model", "=", "hr.covenant"), ("state", "=", "draft")],
                limit=1,
            )
            .id
        )
        vals["stage_id"] = stage_id
        # ToDo
        # covenant.name = self.env["ir.sequence"].next_by_code("hr.covenant.seq")
        return covenant

    def write(self, vals):
        res = super(HrCovenant, self).write(vals)
        for attachment in self.attachment_ids.filtered(
            lambda attachment: not attachment.res_id
        ):
            attachment.res_id = self.id
        return res

    @api.depends("stage_id")
    def _compute_display_button(self):
        for rec in self:
            users = rec._get_approvers()
            rec.display_button_refuse = False
            rec.display_button_accept = False
            rec.display_button_send = False
            if rec.state == "draft" and (
                (rec.create_uid and rec.create_uid.id == rec.env.uid)
                or rec.env.user.has_group("hr.group_hr_manager")
            ):
                rec.display_button_send = True
            elif rec.state == "in_progress" and (
                rec.env.uid in users or rec.env.user.has_group("hr.group_hr_manager")
            ):
                rec.display_button_accept = True
                rec.display_button_refuse = True

    def action_accept(self):
        for covenant in self:
            super(HrCovenant, covenant).action_accept()
            if covenant.state == "done":
                if not covenant.received_date:
                    raise ValidationError(_("Please set the received date"))

    @api.model
    def fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        res = super(HrCovenant, self).fields_view_get(
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

    def name_get(self):
        res = super(HrCovenant, self).name_get()
        for request in self:
            res.append((request.id, request.name))
        return res


class HrCovenantType(models.Model):
    _name = "hr.covenant.type"
    _description = "Covenant Type"

    name = fields.Char(string="name", required=1, translate=True)
    active = fields.Boolean(default=True)


class Employee(models.Model):
    _inherit = "hr.employee"

    covenant_count = fields.Integer(compute="_compute_covenant_count")
    covenant_ids = fields.One2many("hr.covenant", "employee_id", string="Covenants")

    @api.depends("covenant_count")
    def _compute_covenant_count(self):
        for employee in self:
            employee.covenant_count = len(
                employee.covenant_ids.filtered(
                    lambda covenant: covenant.state == "done" and not covenant.retrieval
                )
            )
