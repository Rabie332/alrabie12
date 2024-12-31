{
    "name": "HR Direct Action",
    "version": "14.0.1.0.2",
    "author": "Hadooc",
    "depends": ["request", "hr_base", "hr_employee_number", "request_refuse"],
    "data": [
        "security/ir.model.access.csv",
        "security/direct_action_security.xml",
        "data/hr_direct_action_stage_data.xml",
        "data/mail_data.xml",
        "report/direct_action_report.xml",
        "data/template_mail_data.xml",
        "wizard/hr_direct_action_wizard.xml",
        "views/hr_direct_action_views.xml",
    ],
    "installable": True,
    "license": "AGPL-3",
}
