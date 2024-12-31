from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HrEmployeeBase(models.AbstractModel):
    _inherit = "hr.employee.base"

    number = fields.Char(string="Job number", tracking=True)
    compute_job_number_seq = fields.Boolean(
        string="Compute Job number Sequence",
        related="company_id.automatic_employee_number",
    )

    # ------------------------------------------------------
    # Methods
    # ------------------------------------------------------
    def _get_last_number_by_company(self):
        number = self.search(
            [("company_id", "=", self.company_id.id), ("id", "!=", self.id)],
            order="id desc",
            limit=1,
        ).number
        return number

    # ------------------------------------------------------
    # ORM Methods
    # ------------------------------------------------------
    @api.model
    def create(self, vals):
        """Add employee number by company."""
        employee = super(HrEmployeeBase, self).create(vals)
        if employee and employee.company_id and employee.company_id.sequence_id:
            employee.number = employee.company_id.sequence_id.next_by_id()
        return employee

    def name_get(self):
        """Return the display name of employee.

        ex : [number] name
        """
        res = []
        for emp in self:
            res.append((emp.id, "[{}] {} ".format(emp.number or "", emp.name or "")))
        return res

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        """Search in number,display_name,identification_id."""
        args = args or []
        recs = self.browse()
        if name:
            domain = [
                "|",
                ("number", operator, name),
                ("identification_id", operator, name),
            ]

            recs = self.search(domain + args, limit=limit)
        if not recs:
            recs = self.search([("name", operator, name)] + args, limit=limit)
        return recs.name_get()

    # ------------------------------------------------------
    # Constraint Method
    # ------------------------------------------------------
    @api.constrains("number")
    def _check_number(self):
        """Number should be unique ."""
        for rec in self:
            if rec.number:
                employees = (
                    rec.env["hr.employee"]
                    .sudo()
                    .search(
                        [
                            ("number", "=", rec.number),
                            ("id", "!=", rec.id),
                            ("company_id", "=", rec.company_id.id),
                        ]
                    )
                )
                if employees:
                    raise ValidationError(
                        _("There is an employee with a job number = %s.") % rec.number
                    )


class User(models.Model):
    _inherit = ["res.users"]

    number = fields.Char(
        related="employee_id.number", readonly=True, related_sudo=False
    )

    # pylint: disable=E0101
    def __init__(self, pool, cr):
        """Override of __init__ to add access rights.
        Access rights are disabled by default, but allowed
        on some specific fields defined in self.SELF_{READ/WRITE}ABLE_FIELDS.
        """
        hr_employee_number_readable_fields = ["number"]
        init_res = super(User, self).__init__(pool, cr)
        # duplicate list to avoid modifying the original reference
        type(self).SELF_READABLE_FIELDS = (
            hr_employee_number_readable_fields + type(self).SELF_READABLE_FIELDS
        )
        return init_res
