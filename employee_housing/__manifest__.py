{
    'name': 'Employee Housing',
    'version': '1.0',
    'depends': ['base',
                'mail',
                'account',
                'hr'],
    'author': 'Eng. Fares',
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/housing_building_view.xml',
        'views/housing_unit_type_view.xml',
        'views/housing_unit_view.xml',
        'views/menu.xml'
    ],
}