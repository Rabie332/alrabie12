{
    'name': 'Bayan API',
    'version': '1.0',
    'depends': ['transportation', 'hr', 'clearance', 'base'],
    'author': 'Eng. Fares',
    'data': [
        'security/ir.model.access.csv',
        'views/transportation_views.xml',
        'views/goods_type_views.xml',
        'views/clearance_request_views.xml',
        'views/api_message_wizard_view.xml',
        'views/res_partner_views.xml',
    ],
}