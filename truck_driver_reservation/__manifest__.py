{
    'name': 'Truck And Driver Reservation',
    'version': '1.0',
    'summary': 'Manage reservations of trucks and drivers within the fleet and shipping operations.',
    'category': 'Inventory/Logistics',
    'author': 'Eng. Fares',
    'depends': ['fleet', 'transportation', 'mail'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/truck_driver_reservation_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
