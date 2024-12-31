{
    "name": "Hr Payroll Base",
    "version": "14.0.1.0.0",
    "author": "Hadooc",
    "depends": ["payroll_period", "report_xlsx", "hr_base"],
    "data": [
        "security/hr_payrol_base_security.xml",
        "data/hr_payroll_base_data.xml",
        "views/hr_salary_rule_views.xml",
        "views/hr_payslip_views.xml",
        "views/hr_payroll_structure_views.xml",
        "report/payslip_reports.xml",
        "report/report_payslip_templates.xml",
    ],
    "installable": True,
    "license": "AGPL-3",
    "application": True,
}
