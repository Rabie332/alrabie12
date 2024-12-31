from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResourceResource(models.Model):
    _inherit = "resource.resource"

    name = fields.Char(translate=True)


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    identification_id = fields.Char(size=10, tracking=True)


class HrEmployeeBase(models.AbstractModel):
    _inherit = "hr.employee.base"

    display_name_en = fields.Char(string="English Name", tracking=True)
    identification_date = fields.Date(
        string="National Identity Expiry Date", tracking=True)
    date_direct_action = fields.Date(
        string="Direct Action Date", tracking=True)
    residence_id = fields.Char(
        string="Residence Number", size=10, tracking=True)
    residence_end_date = fields.Date(
        string="Residence Expiration Date", tracking=True)
    passport_end_date = fields.Date(
        string="Passport Expiration Date", tracking=True)
    is_saudian = fields.Boolean(
        string="is saudian", compute="_compute_is_saudian", store=1, tracking=True
    )
    country_id = fields.Many2one(
        "res.country", "Nationality (Country)", tracking=True)

    attachment_ids = fields.Many2many("ir.attachment", string="Attachments")
    expired_stay = fields.Boolean("Expired Stay", tracking=True)
    age = fields.Char(string="Age", compute="_compute_age", tracking=True)
    birthday = fields.Date("Date of Birth", tracking=True)
    insurance_no = fields.Char("Insurance No", tracking=True)
    gosi_no = fields.Char("Gosi No", tracking=True)
    labour_office_no = fields.Char("Labour Office No", tracking=True)
    insurance_attachment_ids = fields.Many2many(
        "ir.attachment",
        "insurance_attachment_rel",
        "insurance_id",
        "attachment_id",
        string="Medical Insurance",
    )
    insurance_end_date = fields.Date(
        string="Medical Insurance Expiration Date", tracking=True)
    health_certificate_attachment_ids = fields.Many2many(
        "ir.attachment",
        "health_certificate_attachment_rel",
        "health_certificate_id",
        "attachment_id",
        string="Health certificate",
    )
    health_certificate_end_date = fields.Date(
        string="Health certificate Expiration Date", tracking=True
    )
    driving_license_attachment_ids = fields.Many2many(
        "ir.attachment",
        "driving_license_attachment_rel",
        "driving_license_id",
        "attachment_id",
        string="Driving licenses",
    )
    driving_license_end_date = fields.Date(
        string="Driving license Expiration Date", tracking=True)

    # ------------------------------------------------------------
    # ORM methods
    # ------------------------------------------------------------

    @api.model
    def create(self, vals):
        employee = super(HrEmployeeBase, self).create(vals)
        # Attach employee to attachment.
        if employee:
            attachments = (
                employee.attachment_ids
                + employee.health_certificate_attachment_ids
                + employee.driving_license_attachment_ids
            )
            attachments.filtered(lambda attachment: not attachment.res_id).write(
                {"res_id": employee.id}
            )
        return employee

    def write(self, vals):
        employee_base = super(HrEmployeeBase, self).write(vals)
        # Attach employee to attachment.
        for employee in self:
            attachments = (
                employee.attachment_ids
                + employee.health_certificate_attachment_ids
                + employee.driving_license_attachment_ids
            )
            attachments.filtered(lambda attachment: not attachment.res_id).write(
                {"res_id": employee.id}
            )
        return employee_base

    # ------------------------------------------------------------
    # Onchange methods
    # ------------------------------------------------------------
    @api.onchange("country_id")
    def onchange_country_id(self):
        self.identification_id = self.residence_id = False

    # ------------------------------------------------------------
    # Compute methods
    # ------------------------------------------------------------

    @api.depends("country_id")
    def _compute_is_saudian(self):
        for rec in self:
            rec.is_saudian = False
            if rec.country_id:
                rec.is_saudian = rec.country_id.code in ("SA", "sa")

    @api.depends("birthday")
    def _compute_age(self):
        """Calculate Employee Age."""
        for emp in self:
            emp.age = ""
            if emp.birthday:
                today_date = fields.Date.from_string(fields.Date.today())
                birthday = fields.Date.from_string(emp.birthday)
                years = (today_date - birthday).days / 354
                if years > -1:
                    emp.age = str(int(years))

    # ------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------

    @api.model
    def _set_expired_stay(self):
        today = fields.Date.context_today(self)
        employees = self.env["hr.employee"].sudo().search([])
        for employee in employees:
            if employee.residence_end_date:
                if employee.residence_end_date <= today:
                    employee.expired_stay = True
                elif (employee.residence_end_date - today).days <= 10:
                    employee.expired_stay = True
                else:
                    employee.expired_stay = False

    # flake8: noqa: C901

    @api.model
    def send_mail_employee_expiration_information(self):
        today = fields.Date.from_string(fields.Date.today())
        employee_settings = (
            self.env["hr.employee.information.setting"].sudo().search([])
        )
        for employee_setting in employee_settings:
            for employee in (
                self.env["hr.employee"]
                .sudo()
                .search([("company_id", "=", employee_setting.company_id.id)])
            ):
                message_header = _(
                    "Name: %s <br/> Job number: %s <br/> Company: %s",
                    employee.name,
                    employee.number,
                    employee.company_id.name,
                )
                # residence notification
                if employee.residence_end_date:
                    users_residence = (
                        employee_setting.user_ids + employee.user_id
                        if employee.user_id
                        and employee.user_id not in employee_setting.user_ids
                        else employee_setting.user_ids
                    )
                    custom_msg_header = _(
                        "<br/> Residence Number: %s <br/> "
                        "Residence Expiration Date: %s <br/><br/>",
                        employee.residence_id,
                        employee.residence_end_date,
                    )
                    if employee_setting.residence_unity == "day":
                        date_residence_notification = (
                            employee.residence_end_date
                            - relativedelta(days=employee_setting.residence)
                        )
                        if date_residence_notification == today:
                            # send mail to users
                            for user in users_residence:
                                mail = (
                                    self.env["mail.mail"]
                                    .sudo()
                                    .create(
                                        {
                                            "subject": _("Residence Expiration"),
                                            "body_html": message_header
                                            + custom_msg_header
                                            + employee_setting.residence_msg,
                                            "email_to": user.email,
                                        }
                                    )
                                )
                                mail.sudo().send()
                    else:
                        date_residence_notification = (
                            employee.residence_end_date
                            - relativedelta(months=employee_setting.residence)
                        )
                        if date_residence_notification == today:
                            # send mail to users
                            for user in users_residence:
                                mail = (
                                    self.env["mail.mail"]
                                    .sudo()
                                    .create(
                                        {
                                            "subject": _("Residence Expiration"),
                                            "body_html": message_header
                                            + custom_msg_header
                                            + employee_setting.residence_msg,
                                            "email_to": user.email,
                                        }
                                    )
                                )
                                mail.sudo().send()
                # passport notification
                if employee.passport_end_date:
                    users_passport = (
                        employee_setting.user_ids + employee.user_id
                        if employee.user_id
                        and employee.user_id not in employee_setting.user_ids
                        else employee_setting.user_ids
                    )
                    custom_msg_header = _(
                        "<br/> Passport No: %s <br/> Passport Expiration Date: %s <br/><br/>",
                        employee.passport_id,
                        employee.passport_end_date,
                    )
                    if employee_setting.passport_unity == "day":
                        date_passport_notification = (
                            employee.passport_end_date
                            - relativedelta(days=employee_setting.passport)
                        )
                        if date_passport_notification == today:
                            # send mail to employee
                            for user in users_passport:
                                mail = (
                                    self.env["mail.mail"]
                                    .sudo()
                                    .create(
                                        {
                                            "subject": _("Passport Expiration"),
                                            "body_html": message_header
                                            + custom_msg_header
                                            + employee_setting.passport_msg,
                                            "email_to": user.email,
                                        }
                                    )
                                )
                                mail.sudo().send()
                    else:
                        date_passport_notification = (
                            employee.passport_end_date
                            - relativedelta(months=employee_setting.passport)
                        )
                        if date_passport_notification == today:
                            # send mail to employee
                            for user in users_passport:
                                mail = (
                                    self.env["mail.mail"]
                                    .sudo()
                                    .create(
                                        {
                                            "subject": _("Passport Expiration"),
                                            "body_html": message_header
                                            + custom_msg_header
                                            + employee_setting.passport_msg,
                                            "email_to": user.email,
                                        }
                                    )
                                )
                                mail.sudo().send()
                # insurance notification
                if employee.insurance_end_date:
                    users_insurance = (
                        employee_setting.user_ids + employee.user_id
                        if employee.user_id
                        and employee.user_id not in employee_setting.user_ids
                        else employee_setting.user_ids
                    )
                    custom_msg_header = _(
                        "<br/> Insurance No: %s <br/> "
                        "Medical Insurance Expiration Date: %s <br/><br/>",
                        employee.insurance_no,
                        employee.insurance_end_date,
                    )
                    if employee_setting.insurance_unity == "day":
                        date_insurance_notification = (
                            employee.insurance_end_date
                            - relativedelta(days=employee_setting.insurance)
                        )
                        if date_insurance_notification == today:
                            # send mail to employee
                            for user in users_insurance:
                                mail = (
                                    self.env["mail.mail"]
                                    .sudo()
                                    .create(
                                        {
                                            "subject": _(
                                                "Medical Insurance Expiration"
                                            ),
                                            "body_html": message_header
                                            + custom_msg_header
                                            + employee_setting.insurance_msg,
                                            "email_to": user.email,
                                        }
                                    )
                                )
                                mail.sudo().send()
                    else:
                        date_insurance_notification = (
                            employee.insurance_end_date
                            - relativedelta(months=employee_setting.insurance)
                        )
                        if date_insurance_notification == today:
                            # send mail to employee
                            for user in users_insurance:
                                mail = (
                                    self.env["mail.mail"]
                                    .sudo()
                                    .create(
                                        {
                                            "subject": _(
                                                "Medical Insurance Expiration"
                                            ),
                                            "body_html": message_header
                                            + custom_msg_header
                                            + employee_setting.insurance_msg,
                                            "email_to": user.email,
                                        }
                                    )
                                )
                                mail.sudo().send()
                # health_certificate notification
                if employee.health_certificate_end_date:
                    users_health_certificate = (
                        employee_setting.user_ids + employee.user_id
                        if employee.user_id
                        and employee.user_id not in employee_setting.user_ids
                        else employee_setting.user_ids
                    )
                    custom_msg_header = _(
                        "<br/> Health certificate Expiration Date: %s <br/><br/>",
                        employee.health_certificate_end_date,
                    )
                    if employee_setting.health_certificate_unity == "day":
                        date_health_certificate_notification = (
                            employee.health_certificate_end_date
                            - relativedelta(days=employee_setting.health_certificate)
                        )
                        if date_health_certificate_notification == today:
                            # send mail to employee
                            for user in users_health_certificate:
                                mail = (
                                    self.env["mail.mail"]
                                    .sudo()
                                    .create(
                                        {
                                            "subject": _(
                                                "Health certificate Expiration"
                                            ),
                                            "body_html": message_header
                                            + custom_msg_header
                                            + employee_setting.health_certificate_msg,
                                            "email_to": user.email,
                                        }
                                    )
                                )
                                mail.sudo().send()
                    else:
                        date_health_certificate_notification = (
                            employee.health_certificate_end_date
                            - relativedelta(months=employee_setting.health_certificate)
                        )
                        if date_health_certificate_notification == today:
                            # send mail to employee
                            for user in users_health_certificate:
                                mail = (
                                    self.env["mail.mail"]
                                    .sudo()
                                    .create(
                                        {
                                            "subject": _(
                                                "Health certificate Expiration"
                                            ),
                                            "body_html": message_header
                                            + custom_msg_header
                                            + employee_setting.health_certificate_msg,
                                            "email_to": user.email,
                                        }
                                    )
                                )
                                mail.sudo().send()
                # date_driving_license_notification notification
                if employee.driving_license_end_date:
                    users_driving_license = (
                        employee_setting.user_ids + employee.user_id
                        if employee.user_id
                        and employee.user_id not in employee_setting.user_ids
                        else employee_setting.user_ids
                    )
                    custom_msg_header = _(
                        "<br/> Driving license Expiration Date: %s <br/><br/>",
                        employee.driving_license_end_date,
                    )
                    if employee_setting.driving_license_unity == "day":
                        date_driving_license_notification = (
                            employee.driving_license_end_date
                            - relativedelta(days=employee_setting.driving_license)
                        )
                        if date_driving_license_notification == today:
                            # send mail to employee
                            for user in users_driving_license:
                                mail = (
                                    self.env["mail.mail"]
                                    .sudo()
                                    .create(
                                        {
                                            "subject": _("Driving license Expiration"),
                                            "body_html": message_header
                                            + custom_msg_header
                                            + employee_setting.driving_license_msg,
                                            "email_to": user.email,
                                        }
                                    )
                                )
                                mail.sudo().send()
                    else:
                        date_driving_license_notification = (
                            employee.driving_license_end_date
                            - relativedelta(months=employee_setting.driving_license)
                        )
                        if date_driving_license_notification == today:
                            # send mail to employee
                            for user in users_driving_license:
                                mail = (
                                    self.env["mail.mail"]
                                    .sudo()
                                    .create(
                                        {
                                            "subject": _("Driving license Expiration"),
                                            "body_html": message_header
                                            + custom_msg_header
                                            + employee_setting.driving_license_msg,
                                            "email_to": user.email,
                                        }
                                    )
                                )
                                mail.sudo().send()

    # ------------------------------------------------------------
    # Constrains
    # ------------------------------------------------------------

    @api.constrains("identification_id")
    def _check_identification_id(self):
        """identification_id should be unique ."""
        for employee in self:
            if employee.identification_id:
                employee_count = employee.env["hr.employee"].search_count(
                    [("identification_id", "=", employee.identification_id)]
                )
                if employee_count > 1:
                    raise ValidationError(
                        _("Identification ID should be unique !"))

    @api.constrains("residence_id")
    def _check_residence_id(self):
        """residence_id should be unique ."""
        for employee in self:
            if employee.residence_id:
                employee_count = employee.env["hr.employee"].search_count(
                    [("residence_id", "=", employee.residence_id)]
                )
                if employee_count > 1:
                    raise ValidationError(_("Residence ID should be unique !"))


class HrEmployeeInformationSetting(models.Model):
    _name = "hr.employee.information.setting"
    _description = "Employee Information Setting"

    name = fields.Char(string="Name", translate=1, required=1, tracking=True)
    residence = fields.Integer("Residence", tracking=True)
    passport = fields.Integer("Passport", tracking=True)
    insurance = fields.Integer("Medical Insurance", tracking=True)
    health_certificate = fields.Integer("Health certificate", tracking=True)
    driving_license = fields.Integer("Driving licenses", tracking=True)
    residence_unity = fields.Selection(
        [("day", "Day"), ("month", "Month")],
        tracking=True,
        default="day",
        string="Residence Unity",
    )
    passport_unity = fields.Selection(
        [("day", "Day"), ("month", "Month")],
        tracking=True,
        default="day",
        string="Passport Unity",
    )
    health_certificate_unity = fields.Selection(
        [("day", "Day"), ("month", "Month")],
        default="day",
        string="Health certificate Unity",
        tracking=True,
    )
    insurance_unity = fields.Selection(
        [("day", "Day"), ("month", "Month")],
        default="day",
        string="Medical Insurance Unity",
        tracking=True,
    )
    driving_license_unity = fields.Selection(
        [("day", "Day"), ("month", "Month")],
        default="day",
        string="Driving license Unity",
        tracking=True,
    )
    residence_msg = fields.Text(
        "Residence Message", translate=1, tracking=True)
    insurance_msg = fields.Text(
        "Medical Insurance Message", translate=1, tracking=True)
    passport_msg = fields.Text("Passport Message", translate=1, tracking=True)
    health_certificate_msg = fields.Text(
        "Health certificate Message", translate=1, tracking=True)
    driving_license_msg = fields.Text(
        "Driving license Message", translate=1, tracking=True)
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
        required=1,
        tracking=True,
    )
    user_ids = fields.Many2many(
        "res.users",
        string="Users",
        domain="[('company_ids', 'in', company_id)]",
        required=1,
    )
