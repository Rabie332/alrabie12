{
    "name": "Hr Attendance Summary",
    "version": "14.0.1.0.0",
    "author": "Hadooc",
    "depends": ["hr_attendance", "hr_holidays", "report_xlsx"],
    "data": [
        "security/hr_attendance_summary_security.xml",
        "security/ir.model.access.csv",
        "data/hr_attendance_summary_data.xml",
        "report/hr_attendance_summary_template.xml",
        "report/hr_attendance_summary_report.xml",
        "wizard/hr_attendance_summary_report_views.xml",
        "views/hr_attendance_notification_views.xml",
        "views/hr_attendance_summary_views.xml",
        "views/res_config_settings_views.xml",
        "views/hr_attendance_summary_line.xml",
        "views/resource_calendar.xml",
        "views/hr_attendance_views.xml",
    ],
    "demo": [],
    "installable": True,
    "auto_install": False,
    "application": False,
    "license": "AGPL-3",
}