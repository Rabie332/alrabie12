{
    "name": "POS VAT report",
    "version": "14.0.1.0.0",
    "author": "Hadooc",
    "license": "AGPL-3",
    "depends": ["point_of_sale"],
    "data": [
        "security/ir.model.access.csv",
        "report/vat_report_templates.xml",
        "report/report.xml",
        "wizard/pos_vat_wizard_views.xml",
    ],
    "installable": True,
}
