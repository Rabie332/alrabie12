{
    "name": "Pos Cash ATM",
    "version": "14.0.1.0.1",
    "category": "Account",
    "author": "Hadooc",
    "depends": ["pos_bank_profit_loss"],
    "data": [
        "security/ir.model.access.csv",
        "reports/pos_sale_report_template.xml",
        "reports/pos_sale_report_views.xml",
        "views/assets.xml",
        "views/pos_session_views.xml",
    ],
    "qweb": [
        "static/src/xml/Popups/*.xml",
        "static/src/xml/Reports/*.xml",
        "static/src/xml/ChromeWidgets/SaleDetailsButton.xml",
    ],
    "installable": True,
    "license": "LGPL-3",
}
