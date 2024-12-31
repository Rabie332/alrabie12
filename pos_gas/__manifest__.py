{
    'name': 'POS Gas Station Prices',
    'version': '1.0',
    'author': "Eng. Fares",
    'category': 'Operations',
    'summary': '',
    'description': """
    """,
    'depends': ['point_of_sale'],
    'data': [
        "views/assets.xml",
        "views/pos_config_views.xml",
    ],
    'qweb': ["static/src/xml/order_receipt.xml"],
    'installable': True,
    'application': True,
}
