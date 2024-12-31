# Copyright 2015 Savoir-faire Linux. All Rights Reserved.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "HR Payroll Period",
    "version": "14.0.2.0.0",
    "category": "Generic Modules/Human Resources",
    "summary": "Add payroll periods",
    "author": "Savoir-faire Linux, " "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/hr",
    "depends": ["hr_payroll", "hr_period"],
    "data": [
        "data/ir_sequence_data.xml",
        "views/hr_payslip_view.xml",
        "views/hr_payslip_run_view.xml",
        "views/menu.xml",
        "views/hr_period_views.xml",
    ],
    "license": "LGPL-3",
}
