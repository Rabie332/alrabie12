{
    "name": "Manage state of accounting",
    "version": "14.0.1.0.2",
    "author": "Hadooc",
    "sequence": 10,
    "category": "Accounting/Accounting",
    "depends": ["account"],
    "data": [
        "data/data_mail.xml",
        "security/account_state_security.xml",
        "views/account_move_views.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
    "license": "AGPL-3",
}
