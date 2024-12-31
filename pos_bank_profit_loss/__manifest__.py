{
    "name": "POS bank profit and loss",
    "version": "14.0.1.0.0",
    "category": "Sales/Point of Sale",
    "author": "Hadooc",
    "license": "AGPL-3",
    "depends": ["pos_no_cash_bank_statement"],
    "data": [
        "security/ir.model.access.csv",
        "views/account_journal_views.xml",
        "views/pos_session_views.xml",
        "views/atm_statement_line_views.xml",
    ],
    "installable": True,
}
