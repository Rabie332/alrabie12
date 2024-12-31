from odoo import fields, models, api


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    sponser_num = fields.Char(string="Sponser Num", tracking=True)
    unified_identification_number = fields.Char(
        string="Unified Identification Number", compute="_compute_unified_identification_number", tracking=True)

    @api.depends('is_saudian', 'identification_id', 'residence_id')
    def _compute_unified_identification_number(self):
        for record in self:
            if record.is_saudian:
                record.unified_identification_number = record.identification_id
            else:
                record.unified_identification_number = record.residence_id

    employee_grade = fields.Selection(
        string="Employee Grade",
        selection=[
            ("grade_1", "Grade 1"),
            ("grade_2", "Grade 2"),
            ("grade_3", "Grade 3"),
            ("grade_4", "Grade 4"),
            ("grade_5", "Grade 5"),
            ("grade_6", "Grade 6"),
            ("grade_7", "Grade 7"),
            ("grade_8", "Grade 8"),
            ("grade_9", "Grade 9"),
            ("grade_10", "Grade 10"),
            ("grade_11", "Grade 11"),
            ("grade_12", "Grade 12"),
            ("grade_13", "Grade 13"),
            ("grade_14", "Grade 14"),
            ("grade_15", "Grade 15"),
            ("grade_16", "Grade 16"),
            ("grade_17", "Grade 17"),
            ("grade_18", "Grade 18"),
            ("grade_19", "Grade 19"),
            ("grade_20", "Grade 20"),
            ("grade_21", "Grade 21"),
            ("grade_22", "Grade 22"),
            ("grade_23", "Grade 23"),
            ("grade_24", "Grade 24"),
            ("grade_25", "Grade 25"),
        ],
        default="grade_1",
        tracking=True
    )
    saudi_job_category = fields.Selection(
        string="Employee Job Position",
        selection=[
            ("ceo", "CEO"),
            ("executive_management", "Executive Management"),
            ("managers", "Managers"),
            ("professionals", "Professionals"),
            ("head", "Head"),
            ("supervisors", "Supervisors"),
            ("senior", "Senior"),
            ("skilled_staff", "Skilled Staff"),
        ],
        default="skilled_staff",
        tracking=True
    )
    non_saudi_job_category = fields.Selection(
        string="Employee Job Position",
        selection=[
            ("executive_management", "Executive Management"),
            ("managers", "Managers"),
            ("professionals", "Professionals"),
            ("head", "Head"),
            ("supervisors", "Supervisors"),
            ("senior", "Senior"),
            ("skilled_staff", "Skilled Staff"),
            ("semi_skilled_staff", "Semi Skilled Staff"),
            ("clerical", "Clerical"),
            ("helper", "Helper"),
            ("housekeeping", "Housekeeping"),
        ],
        default="semi_skilled_staff",
        tracking=True
    )
    employee_level = fields.Selection(
        string="Employee Job Level",
        selection=[
            ("minimum", "Minimum"),
            ("midpoint", "Midpoint"),
            ("maximum", "Maximum"),
        ],
        default="minimum",
        tracking=True
    )

    employee_contract_type = fields.Selection(
        string="Contract Type",
        selection=[
            ("specified", "Specified"),
            ("not_specified", "Not Specified")
        ],
        tracking=True)

    employee_vacation_type = fields.Selection(
        string="Vacation Type",
        selection=[
            ("21", "21"),
            ("30", "30"),
            ("42", "42")
        ],
        tracking=True)
