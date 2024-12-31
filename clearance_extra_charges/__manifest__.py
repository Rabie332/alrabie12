{
    'name': 'Clearance Extra Charges',
    'version': '1.0',
    'summary': 'Handles Extra Charges on Clearance Requests',
    'category': 'clearance',
    'author': 'Eng. Fares',
    'website': 'http://www.farhaholding.com',
    'depends': ['base', 'clearance', 'transportation'],  
    'data': [
        "security/ir.model.access.csv",
        'views/clearance_extra_charges_wizard_views.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
