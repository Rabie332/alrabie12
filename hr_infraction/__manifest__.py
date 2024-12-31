{
    "name": "Employee Infraction Management",
    "version": "14.0.1.0.0",
    "author": "Hadooc",
    "depends": ["hr_period", "request"],
    "data": [
        "security/hr_infraction_security.xml",
        "security/ir.model.access.csv",
        "data/hr_infraction_data.xml",
        "data/hr_infraction_stage_data.xml",
        "views/hr_infraction_views.xml",
        "report/hr_infraction_templates.xml",
        "report/hr_infraction_reports.xml",
    ],
    "installable": True,
    "license": "AGPL-3",
}
