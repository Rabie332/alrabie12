# -*- coding: utf-8 -*-
{
    'name': "Employee Announcements",
    'summary': "Manage employee announcements and notifications",
    'description': """
        This module allows HR managers to create announcements for employees,
        select recipients (users, groups, or departments), schedule sending times,
        and track acknowledgments from the employees. The announcement will
        appear as a pop-up notification to the selected employees, regardless
        of their current Screen within Odoo.
    """,
    'author': "Eng. Fares",
    'category': 'Human Resources',
    'version': '1.0',
    'depends': ['base', 'hr'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/user_notify.xml',
        'views/user_notify_line.xml',
        'views/menus.xml',
        'views/assets.xml',
        'data/cron.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'images': ['static/description/icon.png'],

}
