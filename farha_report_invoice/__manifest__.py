{
    "name": "Farha Report Invoice",
    "version": "14.0.0.0.1",
    "author": "Hadooc",
    "external_dependencies": {"python": ["ummalqura"]},
    "depends": [
        "clearance",
        "invoice_qr_code",
        "web_ar",
    ],
    "data": [
        "report/report.xml",
        "report/account_move_farha_report.xml",
        "views/accout_move_views.xml",
    ],
    "installable": True,
    "license": "AGPL-3",
}
