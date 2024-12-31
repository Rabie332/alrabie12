{
    "name": "HR Financial Covenant",
    "version": "14.0.1.0.1",
    "author": "Eng. Fares",
    "depends": ["request", "hr_employee_number", "request_refuse", "account"],
    "data": [
        "security/ir.model.access.csv",
        "security/financial_covenant_security.xml",
        "data/hr_financial_covenant_data.xml",
        "data/mail_data.xml",
        "views/hr_financial_covenant_views.xml",
        "views/hr_employee_views.xml",
        "views/hr_financial_covenant_setting_views.xml",
    ],
    "installable": True,
    "license": "AGPL-3",
}
