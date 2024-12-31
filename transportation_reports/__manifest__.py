{
    "name": "Transportation Reports",
    "version": "14.0",
    "author": "Eng. Fares",
    "depends": ["transportation", "report_xlsx_helper", "clearance_reports", "clearance", "base"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/transportation_request_wizard_views.xml",
        "report/transportation_request_report_template.xml",
        "views/transportation_request_report_action.xml",
    ],
    "installable": True,
    "license": "AGPL-3",
}