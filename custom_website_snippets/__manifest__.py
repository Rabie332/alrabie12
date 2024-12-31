{
    'name': 'Custom Website Snippets',
    'version': '1.0',
    'summary': 'Adds a custom reusable block to the Website module',
    'sequence': 10,
    'description': """Adds a custom reusable block to the Website module""",
    'category': 'Website',
    'author': 'Eng. Fares',
    'depends': ['website'],
    'data': [
        'views/snippets.xml',
        'views/options.xml', 
        'views/assets.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}