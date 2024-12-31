{
    "name": "Payment Request",
    "version": "14.0.0.0.1",
    "author": "Hadooc",
    "depends": ["request", "account"],
    "data": [
        "security/hr_payment_request_security.xml",
        "security/ir.model.access.csv",
        "data/hr_payment_request_data.xml",
        "data/mail_data.xml",
        "views/menu.xml",
        "views/hr_payment_request_views.xml",
        "views/request_stage_views.xml",
    ],
    "installable": True,
    "license": "AGPL-3",
}
