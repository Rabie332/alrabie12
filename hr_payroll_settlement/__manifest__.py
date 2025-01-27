{
    "name": "Hr Payroll Settlement",
    "version": "14.0.1.0.0",
    "author": "Hadooc",
    "depends": ["hr_payroll_base", "request", "request_refuse", "web_digital_sign"],
    "data": [
        "security/hr_payroll_settlement_security.xml",
        "security/ir.model.access.csv",
        "data/hr_payroll_settlement_data.xml",
        "data/mail_data.xml",
        "report/hr_payroll_settlement_template.xml",
        "report/hr_payroll_settlement_report.xml",
        "views/menu.xml",
        "views/hr_settlement_views.xml",
        "views/request_stage_views.xml",
    ],
    "demo": [],
    "installable": True,
    "application": True,
    "license": "AGPL-3",
}
