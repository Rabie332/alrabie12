# See LICENSE file for full copyright and licensing details.

{
    "name": "Hotel Housekeeping Management",
    "version": "14.0.1.0.0",
    "author": "Odoo Community Association (OCA), Serpent Consulting \
               Services Pvt. Ltd., Odoo S.A.",
    "website": "https://github.com/OCA/vertical-hotel",
    "license": "AGPL-3",
    "summary": "Manages Housekeeping Activities and its Process",
    "category": "Generic Modules/Hotel Housekeeping",
    "depends": ["hotel"],
    "demo": ["views/hotel_housekeeping_data.xml"],
    "data": [
        "security/hotel_housekeeping_security.xml",
        "security/ir.model.access.csv",
        "data/data_mail.xml",
        "report/maintenance_report.xml",
        "report/maintenance_several_report.xml",
        "views/report_hotel_housekeeping.xml",
        "views/hotel_housekeeping_view.xml",
        "views/hotel_floor_views.xml",
        "report/hotel_housekeeping_report.xml",
        "wizard/hotel_housekeeping_wizard.xml",
        "wizard/hotel_housekeeping_maintenance_wizard.xml",
    ],
    "installable": True,
}
