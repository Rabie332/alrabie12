from odoo import _, models, fields, api, exceptions
from datetime import datetime


class UserNotify(models.Model):
    _name = 'user.notify'  # Name of the model
    _description = 'User Notifications'  # Description of the model
    # Inherit mail thread and activity functionality
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Title", required=True,
                       default=None)  # Title of the notification
    # Datetime of the notification
    datetime = fields.Datetime(string="Datetime", default=None, tracking=True)
    # Message body of the notification
    message = fields.Text(string="Message", required=True,
                          default=None, tracking=True)
    dynamic = fields.Boolean(string="Dynamic Post Message", default=False,
                             copy=False, tracking=True)  # Flag for dynamic notification
    users = fields.One2many('res.users', 'notify_id', string="Users",
                            default=None, tracking=True)  # Many2one relation with res.users
    groups = fields.One2many('res.groups', 'notify_id', string="Groups",
                             default=None, tracking=True)  # Many2one relation with res.groups
    departments = fields.One2many('hr.department', 'notify_id', string="Departments",
                                  default=None, tracking=True)  # Many2one relation with hr.department
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('cancel', 'Cancel')
    ], default='draft', tracking=True)  # State of the notification
    recipient_type = fields.Selection([
        ('user', 'Users'),
        ('group', 'Groups'),
        ('department', 'Departments'),
    ], string="Type of Recipients", required=True, tracking=True)  # Type of recipients for the notification
    # One2many relation with user.notify.line
    notification_line = fields.One2many('user.notify.line', 'notification_id')
    notification_line_count = fields.Integer(
        string='Users Count', compute='_compute_notification_line_count')  # Compute field for counting notification lines

    @api.model
    def resend_unread_notifications(self):
        """Method to resend unread notifications every 3 hours."""
        # Search for all active notifications
        notifications = self.search([('state', '=', 'active')])
        for notification in notifications:
            # Resend the notification to unread users
            unread_lines = notification.notification_line.filtered(
                lambda line: line.state == 'unread')
            for line in unread_lines:
                notification.notify(line.user.partner_id.id,
                                    notification.name, notification.message)

    @api.depends('notification_line')  # Depends on notification_line field
    def _compute_notification_line_count(self):
        for record in self:
            # Set the count of notification lines
            record.notification_line_count = len(record.notification_line)

    def action_go_to_notification_lines(self):
        self.ensure_one()  # Ensure that only one record is selected
        # Open the notification Users for the selected record
        return {
            'type': 'ir.actions.act_window',
            'name': _('Notification Users'),
            'view_mode': 'tree',
            'res_model': 'user.notify.line',
            'domain': [('notification_id', '=', self.id)],
            # Disable create and edit buttons
            'context': {'create': False, 'edit': False},
        }

    def set_active(self):
        if self.state == 'draft':
            self.write({'state': 'active'})  # Set the state to 'active'

    def set_cancel(self):
        if self.state != 'cancel':
            self.write({'state': 'cancel'})  # Set the state to 'cancel'

    def change_action(self):
        if self.datetime:
            cornjob = self.env['ir.cron'].with_context(active_test=False).search(
                [('name', '=', 'Dynamic Notification (%s): %s ' % (self.id, self.name))], limit=1)  # Search for an existing cron job
            if self.dynamic == False:
                self.write({'dynamic': True})  # Set dynamic button to True
                if cornjob:
                    cornjob.write({
                        'active': True,
                        'nextcall': self.datetime,
                        'numbercall': 1,
                    })  # Active the existing cron job
                else:
                    self.env['ir.cron'].create({
                        'name': 'Dynamic Notification (%s): %s ' % (self.id, self.name),
                        'model_id': self.env.ref('announcements.model_user_notify').id,
                        'state': 'code',
                        'active': True,
                        'nextcall': self.datetime,
                        'code': "model.send_msg(%s)" % self.id,
                        'numbercall': 1,
                        'interval_number': 1,
                        'interval_type': 'minutes',
                        'doall': 0,
                    })  # Create a new cron job for dynamic notification
            else:
                self.write({'dynamic': False})  # Set dynamic button to False
                if cornjob:
                    cornjob.write({
                        'active': False,
                        'numbercall': 0
                    })  # Deactivate the existing cron job
        else:
            # Raise a validation error if datetime is not set
            raise exceptions.ValidationError(
                _("You must set datetime to schedule the procedure"))

    def send_msg(self, id=None):
        if not id:
            id = self.id  # If no id is provided, use the current record's id
        # Search for the notification record
        rec = self.env['user.notify'].search([('id', '=', id)])
        if rec.state == 'active':
            for line in rec.notification_line:
                if line.state == 'unread':
                    # Send notification to the user's partner if its state is unread
                    rec.notify(line.user.partner_id.id, rec.name, rec.message)

    def notify(self, user, title, message):
        self.env['bus.bus'].sendone(
            (self._cr.dbname, 'res.partner', user),
            {
                'type': 'announcements_dialog',
                'title': title,
                'message': message,
                'id': self.id,
            }
        )
        return True

    @api.model
    def close_notify(self, id):
        line_ids = self.env['user.notify'].sudo().search(
            [('id', '=', id)])  # Search for the notification record
        for line in line_ids:
            users = line.notification_line.filtered(
                lambda record: record.user.id == self.env.user.id)
            for user in users:
                if user.state == 'unread':
                    user.write({
                        'state': 'read',
                        'datetime': datetime.now()
                    })  # Mark the notification as 'read' for the user who closes the notification popup
        return True

    @api.model
    def create(self, vals):
        record = super(UserNotify, self).create(
            vals)  # Override Create Function
        line_ids = record.env['user.notify.line']
        if record.recipient_type == 'user':
            for user in record.users:
                # Create notification lines for users
                line_ids.create(
                    {'notification_id': record.id, 'user': user.id})
        if record.recipient_type == 'group':
            users = self.env['res.users'].search(
                [('groups_id', 'in', record.groups.ids)])
            for user in users:
                # Create notification lines for groups
                line_ids.create(
                    {'notification_id': record.id, 'user': user.id})
        if record.recipient_type == 'department':
            employees = self.env['hr.employee'].search(
                [('department_id', 'in', record.departments.ids)])
            for emp in employees:
                if emp.user_id:
                    # Create notification lines for departments
                    line_ids.create(
                        {'notification_id': record.id, 'user': emp.user_id.id})
        return record

    def write(self, vals):
        record = super(UserNotify, self).write(
            vals)  # Override Update Function
        if record:
            line_ids = self.env['user.notify.line'].search(
                [('notification_id', '=', self.id)])
            if line_ids:
                line_ids.unlink()  # Remove existing notification lines
            if self.recipient_type == 'user':
                for user in self.users:
                    # Create new notification lines for users
                    line_ids.create(
                        {'notification_id': self.id, 'user': user.id})
            if self.recipient_type == 'group':
                users = self.env['res.users'].search(
                    [('groups_id', 'in', self.groups.ids)])
                for user in users:
                    # Create new notification lines for groups
                    line_ids.create(
                        {'notification_id': self.id, 'user': user.id})
            if self.recipient_type == 'department':
                employees = self.env['hr.employee'].search(
                    [('department_id', 'in', self.departments.ids)])
                for emp in employees:
                    if emp.user_id:
                        # Create new notification lines for departments
                        line_ids.create(
                            {'notification_id': self.id, 'user': emp.user_id.id})
        return record


class UserNotifyLine(models.Model):
    _name = 'user.notify.line'
    _description = 'User Notification Lines'

    # Many2one relation with user.notify
    notification_id = fields.Many2one('user.notify')
    # Many2one relation with res.users (required)
    user = fields.Many2one('res.users', required=True)
    state = fields.Selection([
        ('unread', 'Unread'),
        ('read', 'Read')
    ], default='unread')  # State of the notification line (unread or read)
    datetime = fields.Datetime(default=None)


class ResUser(models.Model):
    _inherit = 'res.users'
    # Many2one relation with user.notify
    notify_id = fields.Many2one('user.notify')


class ResGroup(models.Model):
    _inherit = 'res.groups'
    # Many2one relation with user.notify
    notify_id = fields.Many2one('user.notify')


class hrDepartment(models.Model):
    _inherit = 'hr.department'
    # Many2one relation with user.notify
    notify_id = fields.Many2one('user.notify')
