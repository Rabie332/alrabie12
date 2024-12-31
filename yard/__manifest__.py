{
    "name": "Yard",
    "version": "1.1",
    'license': 'LGPL-3',
    "author": "Eng. Fares",
    "summary": "Yard Management System",
    "description": "This is Yard management system software supported in Odoo v14",
    "category": "Yard",
    "website": "https://engfaresalharbi.in",
    'depends': ['base', 'fleet', 'product', 'clearance', 'transportation', 'mail'],
    'application': True,
    "data": [
        "security/ir.model.access.csv",
        "views/yard_menu.xml",
        "views/yard_zone_views.xml",
        "views/yard_container_views.xml",
        "views/yard_blocks_views.xml",
        'views/shipping_order_view.xml'
    ],
}
