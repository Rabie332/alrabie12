{
    "name": "HR Covenant",
    "version": "14.0.1.0.0",
    "author": "Hadooc",
    "depends": ["request", "base", "hr_employee_number", "report_xlsx"],
    "data": [
        "security/ir.model.access.csv",
        "security/covenant_security.xml",
        "data/hr_covenant_type_data.xml",
        "data/hr_covenant_data.xml",
        "data/mail_data.xml",
        "views/hr_covenant_views.xml",
        "views/hr_employee_views.xml",
        "wizard/hr_covenant_wizard_views.xml",
        "report/hr_covenant_templates.xml",
        "report/hr_covenant_reports.xml",
    ],
    "installable": True,
    "license": "AGPL-3",
}