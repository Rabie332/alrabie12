# Corrected manifest file __manifest__.py

{
    'name': 'Helpdesk',
    'version': '1.1',
    'license': 'LGPL-3',
    'author': 'Eng. Fares',
    'summary': 'IT Ticketing System',
    'description': """
        This module provides a comprehensive IT ticketing system. 
        It allows for the creation, assignment, and management of IT support tickets within Odoo v14.
        Features include prioritization, departmental assignment, and integration with Odoo's email subsystem.
    """,
    'category': 'Helpdesk',
    'website': 'https://engfaresalharbi.in',
    # Ensure these dependencies are correct and the modules are installed.
    'depends': ['base', 'hr', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        # 'security/security',
        'views/it_tickets_view.xml',  # View definitions for the IT Tickets
        'views/it_ticket_stages_data.xml'
    ],
    'demo': [  # You can include demo data for testing and demonstration purposes.
        # 'demo/demo_data.xml',
    ],
    'images': [  # Screenshots or icons of the module.
        # 'static/description/icon.png',
        # 'static/description/screenshot.png',
    ],
    'installable': True,  # Module can be installed.
    # This is a standalone application and not just a technical module.
    'application': True,
    # This module won't be installed automatically when its dependencies are installed.
    'auto_install': False,
    'sequence': 10,  # Sequence for module loading, lower number loads first.
    # 'external_dependencies': {'python': ['library_name'], 'bin': []},  # If your module depends on external libraries
}
