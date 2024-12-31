{
    'name': 'Delete Partner Inovices Wizard',
    'version': '1.0',
    'summary': 'Delete Partner Inovices',
    'category': 'accounting',
    'author': 'Eng. Fares',
    'website': 'http://www.farhaholding.com',
    'depends': ['base', 'account'],
    'data': [
        "security/ir.model.access.csv",
        'views/account_move_view.xml',
        'views/delete_all_partner_invoices_view.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
