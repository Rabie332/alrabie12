from odoo import models, fields, api, _
import logging
from datetime import timedelta  # Importing timedelta

_logger = logging.getLogger(__name__)


class CustomPurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    delivery_location = fields.Many2one(
        'res.company', string="Delivery Location", store=True, tracking=True
    )
    assign_to_purchase_dept_employee = fields.Many2one(
        'hr.employee', string="Assign it to Employee", store=True, tracking=True,
        domain=lambda self: self._get_subordinate_domain()
    )
    in_inventory = fields.Selection(
        [("available", "Available"), ("not available", "Not Available")], index=True, tracking=True,
    )
    show_in_inventory = fields.Boolean(compute='_compute_show_in_inventory')
    show_in_purchase_dep = fields.Boolean(
        compute='_compute_show_in_purchase_dep')
    po_ids = fields.One2many(
        'purchase.order', 'purchase_request_id', string='Purchase Orders', readonly=True, copy=False, store=True
    )
    po_count = fields.Integer(
        string='Purchase Orders Count', compute='_compute_po_count')
    show_to_draft_button = fields.Boolean(
        compute='_compute_show_to_draft_button')
    show_pm_director_ceo_stages = fields.Boolean(
        compute="_compute_pm_director_ceo_stages")

    @api.depends('po_ids')
    def _compute_po_count(self):
        for request in self:
            request.po_count = len(request.po_ids)

    def action_view_purchase_orders(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Purchase Orders',
            'view_mode': 'tree,form',
            'res_model': 'purchase.order',
            'domain': [('purchase_request_id', '=', self.id)],
            'context': {'default_purchase_request_id': self.id},
        }

    @api.depends('stage_id')
    def _compute_show_in_inventory(self):
        for record in self:
            record.show_in_inventory = record.stage_id.name in [
                'Inventory', 'المستودع']

    @api.depends('stage_id')
    def _compute_show_in_purchase_dep(self):
        for record in self:
            if self.env.user.has_group('custom_purchase_request.group_purchase_request_admin'):
                record.show_in_purchase_dep = record.stage_id.name in [
                    'Purchase Department', 'قسم المشتريات']
            else:
                record.show_in_purchase_dep = False

    @api.model
    def _get_subordinate_domain(self):
        stage = self.env['request.stage'].search([
            '|', ('name', '=', 'Purchase Manager'), ('name', '=', 'مدير المشتريات')
        ], limit=1)
        if stage.default_user_id:
            manager_employee = self.env['hr.employee'].search([
                ('user_id', '=', stage.default_user_id.id)
            ], limit=1)
            if manager_employee:
                return [('id', 'child_of', manager_employee.id)]
        return []

    @api.model
    def create(self, vals):
        res = super(CustomPurchaseRequest, self).create(vals)
        res._create_activity_if_needed()
        return res

    def write(self, vals):
        res = super(CustomPurchaseRequest, self).write(vals)
        self._create_activity_if_needed()
        return res

    def _create_activity_if_needed(self):
        for request in self:
            if request.stage_id.name in ['Purchase Department', 'قسم المشتريات'] and request.assign_to_purchase_dept_employee:
                self.env['mail.activity'].create({
                    'activity_type_id': self.env.ref('mail.mail_activity_data_todo').id,
                    'summary': _('Follow up on Purchase Request'),
                    'user_id': request.assign_to_purchase_dept_employee.user_id.id,
                    'res_model_id': self.env['ir.model']._get_id('purchase.request'),
                    'res_id': request.id,
                    'date_deadline': fields.Date.context_today(request) + timedelta(days=7),
                })

    def action_reset_to_draft(self):
        draft_stage_id = self.env['request.stage'].search([
            '|', ('name', '=', 'Purchase Request'), ('name', '=', 'طلب الشراء')], limit=1).id
        if draft_stage_id:
            self.write({'state': 'draft', 'stage_id': draft_stage_id})
            if not self.name:
                new_name = self.env['ir.sequence'].next_by_code(
                    'purchase.request.seq')
                self.write({'name': new_name})

    def action_reset_to_pm(self):
        pm_stage_id = self.env['request.stage'].search([
            '|', ('name', '=', 'Purchase Manager'), ('name', '=', 'مدير المشتريات')], limit=1).id
        for request in self:
            if request.stage_id:
                request.stage_id = pm_stage_id
                request._onchange_stage_id()
                if request.state != "done":
                    request.activity_update()
                else:
                    request.action_feedback()
        return True

    def action_reset_to_director(self):
        director_stage_id = self.env['request.stage'].search([
            '|', ('name', '=', 'Director'), ('name', '=', 'مدير الخدمات المشتركة')], limit=1).id
        for request in self:
            if request.stage_id:
                request.stage_id = director_stage_id
                request._onchange_stage_id()
                if request.state != "done":
                    request.activity_update()
                else:
                    request.action_feedback()
        return True

    def action_reset_to_complete(self):
        complete_stage_id = self.env['request.stage'].search([
            '|', ('name', '=', 'Complete'), ('name', '=', 'مكتمل')], limit=1).id
        if complete_stage_id:
            self.write({'state': 'done', 'stage_id': complete_stage_id})
            if not self.name:
                new_name = self.env['ir.sequence'].next_by_code(
                    'purchase.request.seq')
                self.write({'name': new_name})

    def move_pr_to_complete(self):
        purchase_department_stage_id = self.env['request.stage'].search([
            '|', ('name', '=', 'Purchase Manager'), ('name',
                                                     '=', 'مدير المشتريات'),
            '|', ('name_dept', '=', 'Purchase Department'), ('name_dept', '=', 'قسم المشتريات')], limit=1).id
        complete_stage_id = self.env['request.stage'].search([
            '|', ('name', '=', 'Complete'), ('name', '=', 'مكتمل')], limit=1).id

        if purchase_department_stage_id and complete_stage_id:
            prs_in_purchase_department = self.search(
                [('stage_id', '=', purchase_department_stage_id)])
            for pr in prs_in_purchase_department:
                pr.write({'stage_id': complete_stage_id})
                # Add any additional logic if needed, e.g., logging, notifications, etc.
            return True
        else:
            return False

    def create_purchase_order(self):
        selected_lines = self.line_ids.filtered(lambda l: l.PO_checkbox_field)
        if not selected_lines:
            _logger.error("No lines selected for PO creation.")
            return

        vendor_id = selected_lines._find_vendor()
        if not vendor_id:
            _logger.error("No vendor found for selected lines.")
            return

        purchase_order = self.env['purchase.order'].create({
            'partner_id': vendor_id,
            'date_order': fields.Datetime.now(),
            'purchase_request_id': self.id,
        })
        _logger.info(f"Created PO ID: {purchase_order.id}")

        selected_lines._create_po_lines(purchase_order)

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'res_id': purchase_order.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_not_in_inventory(self):
        stage_domain = [
            '|', ('name', '=', 'CEO'), ('name', '=', 'الرئيس التنفيذي'),
            '|', ('name_dept', '=', 'Purchase Department'), ('name_dept',
                                                             '=', 'قسم المشتريات')
        ]

        if self.estimated_budget <= 29999:
            stage_domain = [
                '|', ('name', '=', 'Purchase Manager'), ('name',
                                                         '=', 'مدير المشتريات'),
                '|', ('name_dept', '=',
                      'Purchase Department'), ('name_dept', '=', 'قسم المشتريات')
            ]
        elif self.estimated_budget <= 49999:
            stage_domain = [
                '|', ('name', '=', 'Director'), ('name',
                                                 '=', 'مدير الخدمات المشتركة'),
                '|', ('name_dept', '=',
                      'Purchase Department'), ('name_dept', '=', 'قسم المشتريات')
            ]

        ceo_stage_id = self.env['request.stage'].search(
            stage_domain, limit=1).id

        for request in self:
            if request.stage_id and request.state == "in_progress":
                request.stage_id = ceo_stage_id
                request._onchange_stage_id()
                if request.state != "done":
                    request.activity_update()
                else:
                    request.action_feedback()
        return True

    @api.depends('stage_id')
    def _compute_pm_director_ceo_stages(self):
        for record in self:
            users = record._get_approvers()
            record.show_pm_director_ceo_stages = False
            if record.env.uid in users:
                record.show_pm_director_ceo_stages = record.stage_id.name in [
                    'Purchase Manager', 'مدير المشتريات', 'Director', 'مدير الخدمات المشتركة', 'CEO', 'الرئيس التنفيذي']

    def action_pm_director_ceo_stages(self):
        pd_stage_id = self.env['request.stage'].search([
            '|', ('name', '=', 'Purchase Department'), ('name',
                                                        '=', 'قسم المشتريات'),
            '|', ('name_dept', '=', 'Purchase Department'), ('name_dept',
                                                             '=', 'قسم المشتريات')
        ], limit=1).id

        for request in self:
            if request.stage_id and request.state == "in_progress":
                request.stage_id = pd_stage_id
                request._onchange_stage_id()
                if request.state != "done":
                    request.activity_update()
                else:
                    request.action_feedback()
        return True

    def _compute_show_to_draft_button(self):
        for record in self:
            record.show_to_draft_button = False
            if (record.state in ['in_progress', 'cancel', 'done']) and self.env.user.has_group('custom_purchase_request.group_purchase_request_admin'):
                record.show_to_draft_button = True


class CustomPurchaseRequestLine(models.Model):
    _inherit = 'purchase.request.line'

    PO_checkbox_field = fields.Boolean(string="Create PO", default=False)
    show_in_purchase_dep = fields.Boolean(
        compute='_compute_show_in_purchase_dep')

    @api.depends('purchase_request_id')
    def _compute_show_in_purchase_dep(self):
        for record in self:
            record.show_in_purchase_dep = record.purchase_request_id.stage_id.name in [
                'Purchase Department', 'قسم المشتريات']

    def _find_vendor(self):
        for line in self.filtered(lambda l: l.PO_checkbox_field):
            if line.product_id.seller_ids:
                return line.product_id.seller_ids[0].name.id
        return False

    def _create_po_lines(self, purchase_order):
        for line in self:
            self.env['purchase.order.line'].create({
                'order_id': purchase_order.id,
                'product_id': line.product_id.id,
                'product_qty': line.product_qty,
                'product_uom': line.product_uom_id.id,
                'price_unit': line.product_id.standard_price,
            })


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    purchase_request_id = fields.Many2one(
        'purchase.request', string='Purchase Request', readonly=True)
