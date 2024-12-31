{
    "name": "Account Move Report",
    "version": "14.0.1.0.0",
    "author": "Hadooc",
    "depends": ["account_state", "report_xlsx"],
    "data": [
        "security/ir.model.access.csv",
        "report/account_move_report.xml",
        "report/account_entry_template.xml",
        "report/reports.xml",
        "views/account_move_views.xml",
        "wizard/account_entry_report_wizard_views.xml",
    ],
    "installable": True,
    "auto_install": True,
    "license": "AGPL-3",
}
