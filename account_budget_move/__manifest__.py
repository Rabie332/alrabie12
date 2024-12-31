{
    "name": "Account Budget Move",
    "version": "14.0.1.0.0",
    "author": "Hadooc",
    "depends": ["account_budget_oca", "account_state"],
    "data": [
        "security/ir.model.access.csv",
        "data/account_budget_move_data.xml",
        "views/crossovered_budget_move_views.xml",
    ],
    "installable": True,
    "application": True,
    "license": "AGPL-3",
}
