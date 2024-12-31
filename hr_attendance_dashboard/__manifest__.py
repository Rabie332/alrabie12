{
    "name": "Hr Attendance Dashboard",
    "version": "14.0.1.0.0",
    "author": "Hadooc",
    "depends": [
        "hr_attendance_summary",
        "hr_public_holidays",
        "hr_authorization",
        "dashboard_base",
    ],
    "data": [
        "views/assets.xml",
        "views/menus.xml",
    ],
    "qweb": ["static/src/xml/dashboard_templates.xml"],
    "installable": True,
    "auto_install": False,
    "application": False,
    "license": "AGPL-3",
}
