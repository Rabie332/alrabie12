{
    "name": "HR Profile",
    "version": "14.0.1.0.0",
    "author": "Hadooc",
    "depends": ["request", "hr_contract", "hr_holidays"],
    "data": [
        "security/ir.model.access.csv",
        "views/hr_profile_views.xml",
        "views/res_users_views.xml",
    ],
    "installable": True,
    "application": True,
    "license": "AGPL-3",
}
