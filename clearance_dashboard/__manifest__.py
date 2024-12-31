{
    "name": "Clearance Dashboard",
    "version": "14.0.1.0.0",
    "author": "Eng. Fares",
    "depends": [
        "dashboard_base",
        "transportation",
    ],
    "data": [
        "security/clearance_dashboard_security.xml",
        "security/ir.model.access.csv",
        "views/dashboard_views.xml",
    ],
    "qweb": [
        "static/src/xml/transportation_dashboard.xml",
        "static/src/xml/clearance_dashboard.xml",
    ],
    "installable": True,
    "license": "AGPL-3",
}
