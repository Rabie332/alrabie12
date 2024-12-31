from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    birthday = fields.Date(required=1, tracking=True)
    job_title = fields.Char(required=1, tracking=True)

    department_id = fields.Many2one(required=1, tracking=True)
    country_id = fields.Many2one(required=1, tracking=True)
    parent_id = fields.Many2one(required=1, tracking=True)
    guarantor_company = fields.Char(string="Guarantor Company", tracking=True)
    is_not_gosi_no = fields.Boolean(
        string="Gosi No Data", compute="_compute_icon_visibility", tracking=True
    )
    is_not_labour_office_no = fields.Boolean(
        string="Labour Office No Data", compute="_compute_icon_visibility", tracking=True
    )
    is_not_residence_id = fields.Boolean(
        string="Residence Data", compute="_compute_icon_visibility", tracking=True
    )
    is_not_insurance_no = fields.Boolean(
        string="Insurance No Data", compute="_compute_icon_visibility", tracking=True
    )
    is_not_bank_account_id = fields.Boolean(
        string="Bank Account Data", compute="_compute_icon_visibility", tracking=True
    )

    def _compute_icon_visibility(self):
        """To check if the fields bellow are filled"""
        for employee in self:
            employee.is_not_gosi_no = False
            employee.is_not_labour_office_no = False
            employee.is_not_residence_id = False
            employee.is_not_insurance_no = False
            employee.is_not_bank_account_id = False
            if not employee.gosi_no:
                employee.is_not_gosi_no = True
            if not employee.labour_office_no:
                employee.is_not_labour_office_no = True
            if (
                not employee.residence_id
                and employee.country_id
                and employee.country_id.code != "SA"
            ):
                employee.is_not_residence_id = True
            if not employee.insurance_no:
                employee.is_not_insurance_no = True
            if not employee.bank_account_id:
                employee.is_not_bank_account_id = True

    @api.onchange("driving_license_end_date")
    def _onchange_driving_license_end_date(self):
        """Update driving license end date of fleet."""
        if self.driving_license_end_date and (
            self.address_home_id or self.user_id.partner_id
        ):
            driver_ids = []
            if self.user_id.partner_id:
                driver_ids.append(self.user_id.partner_id.id)
            if self.address_home_id:
                driver_ids.append(self.address_home_id.id)
            fleets = self.env["fleet.vehicle"].search([("driver_id", "in", driver_ids)])
            if fleets:
                fleets.write(
                    {"driver_license_expiry_date": self.driving_license_end_date}
                )
