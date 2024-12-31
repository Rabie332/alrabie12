from odoo import models, fields, api


class Tickets(models.Model):
    _name = 'it.tickets'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'IT Tickets'

    name = fields.Char(string='Ticket Title', required=True,
                       index=True, tracking=True)
    assigned_to = fields.Selection(
        [('odoo team', 'Odoo Team'), ('helpdesk team', 'Helpdesk Team')],
        string='Assigned To', tracking=True, required=True
    )
    kind_of_odoo_probelm = fields.Selection(
        [('system error', 'System Error'), ('new feature', 'New Feature')],
        tracking=True, string="Kind Of Odoo Probelm", index=True
    )
    ticket_department = fields.Many2one(
        'hr.department', string="Department", compute='_compute_department', store=True,
    )
    create_date = fields.Datetime("Ticket Date")
    employee_id = fields.Many2one('hr.employee.public',
                                  string='Employee',
                                  default=lambda self: self._default_employee(),
                                  )
    ticket_description = fields.Text(
        string="Description", tracking=True, required=True)

    state = fields.Selection(
        [("draft", "Draft"), ("on hold", "On Hold"), ("in progress", "In Progress"),
         ("resolved", "Resolved"), ("denied", "Denied")],
        default="draft", index=True, tracking=True
    )
    stage_id = fields.Many2one(
        'it.ticket.stage', string="Stage", compute='_compute_stage_id', store=True, group_expand='_read_group_stage_ids'
    )
    active = fields.Boolean(string="Active", default=True)

    show_to_draft_button = fields.Boolean(compute='_compute_show_to_draft_button')

    def _compute_show_to_draft_button(self):
        for record in self:
            # Set the default to False
            record.show_to_draft_button = False

            # Check if the user is in the specific group for "on hold" state
            if record.state == 'on_hold' and self.env.user.has_group('help_desk.group_helpdesk_admin'):
                record.show_to_draft_button = True

            # Check if the user is in the specific group for "denied" state
            elif record.state == 'denied' and self.env.user.has_group('help_desk.group_helpdesk_admin'):
                record.show_to_draft_button = True
                
    @api.depends('state')
    def _compute_stage_id(self):
        for ticket in self:
            stage = self.env['it.ticket.stage'].search(
                [('name', '=', ticket.state.title())], limit=1)
            ticket.stage_id = stage

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        stage_ids = self.env['it.ticket.stage'].search([])
        return stage_ids

    def to_on_hold(self):
        self.state = 'on hold'

    def to_in_progress(self):
        self.state = 'in progress'

    def to_resolved(self):
        self.state = 'resolved'

    def to_denied(self):
        self.state = 'denied'

    def to_draft(self):
        self.state = 'draft'

    @api.model
    def _default_employee(self):
        # Logic to return the default hr.employee record based on the current user
        user = self.env.user
        employee = self.env['hr.employee'].search(
            [('user_id', '=', user.id)], limit=1)
        return employee

    @api.depends('employee_id')
    def _compute_department(self):
        for record in self:
            record.ticket_department = record.employee_id.department_id if record.employee_id else False
