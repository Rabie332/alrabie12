from lxml import etree

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HrFinancialCovenant(models.Model):
    _name = "hr.financial.covenant"
    _inherit = ["request"]
    _description = "Financial Covenant"
    _order = "date"

    financial_covenant_number = fields.Char(string="Covenant Number", readonly=1)
    employee_id = fields.Many2one(
        "hr.employee",
        string="Employee",
        required=1,
        readonly=1,
        states={"draft": [("readonly", 0)]},
    )
    reason = fields.Char(
        "Reason", required=1, readonly=1, states={"draft": [("readonly", 0)]}
    )
    required_value = fields.Float(
        "Amount",
        required=1,
        readonly=0,
        states={"cancel": [("readonly", 1)], "done": [("readonly", 1)]},
    )

    number = fields.Char(string="Job number", readonly=1)
    name = fields.Char(required=1, readonly=1, states={"draft": [("readonly", 0)]})
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
        readonly=1,
        states={"draft": [("readonly", 0)]},
    )
    refuse_reason = fields.Char(string="Refusal reason")
    account_move_id = fields.Many2one(
        "account.move", string="Entry", readonly=True, copy=False
    )
    is_paid = fields.Boolean(default=False)

    @api.model
    def create(self, values):
        """ADD sequence to Financial Covenant"""
        financial_covenant = super(HrFinancialCovenant, self).create(values)
        if financial_covenant:
            # ADD sequence to company
            if not financial_covenant.company_id.financial_covenant_sequence_id:
                IrSequence = self.env["ir.sequence"].sudo()
                val = {
                    "name": "Sequence Financial Covenant "
                    + financial_covenant.company_id.name,
                    "padding": 5,
                    "code": "hr.financial.covenant.seq",
                }
                financial_covenant.company_id.sudo().financial_covenant_sequence_id = (
                    IrSequence.create(val).id
                )
            # ADD sequence to Financial Covenant
            financial_covenant.financial_covenant_number = (
                financial_covenant.company_id.financial_covenant_sequence_id.next_by_id()
            )
        return financial_covenant

    def _sync_employee_details(self):
        super(HrFinancialCovenant, self)._sync_employee_details()
        for request in self:
            if request.employee_id:
                request.number = request.employee_id.number
                request.company_id = request.employee_id.company_id.id

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
            super(HrFinancialCovenant, covenant).action_accept()
            if covenant.state == "done":
                setting = (
                    covenant.env["hr.financial.covenant.setting"]
                    .search([], limit=1)
                    .financial_covenant_move_ids.filtered(
                        lambda line: line.company_id == covenant.company_id
                        or not line.company_id
                    )
                )
                if setting:
                    setting = setting[0]
                else:
                    raise ValidationError(
                        _("Must add accounting financial covenant setting.")
                    )
                partner = False
                if covenant.employee_id.address_home_id:
                    partner = covenant.employee_id.address_home_id.id
                elif covenant.employee_id.user_id:
                    partner = covenant.employee_id.user_id.partner_id.id
                move = (
                    self.env["account.move"]
                    .sudo()
                    .create(
                        {
                            "move_type": "entry",
                            "journal_id": setting.journal_id.id,
                            "line_ids": [
                                (
                                    0,
                                    0,
                                    {
                                        "account_id": setting.account_id.id,
                                        "name": covenant.name,
                                        "partner_id": partner,
                                        "debit": covenant.required_value,
                                        "credit": 0.0,
                                    },
                                ),
                                (
                                    0,
                                    0,
                                    {
                                        "account_id": setting.journal_id.default_account_id.id,
                                        "partner_id": partner,
                                        "name": covenant.name,
                                        "debit": 0.0,
                                        "credit": covenant.required_value,
                                    },
                                ),
                            ],
                        }
                    )
                )
                covenant.account_move_id = move.id

    
    def action_reset_to_draft(self):
        draft_stage_id = self.env['request.stage'].search([
            '|', ('name', '=', 'draft'), ('name', '=', 'مسودة'),
            '|', ('name_dept', '=', 'Covenant Stage'), ('name_dept', '=', 'Covenant Stage')
        ], limit=1).id
        if draft_stage_id:
            self.write({'state': 'draft', 'stage_id': draft_stage_id})
    @api.model
    def fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        res = super(HrFinancialCovenant, self).fields_view_get(
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
