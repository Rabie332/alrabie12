{
    "name": "POS later payment",
    "version": "14.0.0.0.0",
    "category": "Point of Sale",
    "author": "Eng. Fares",
    "license": "AGPL-3",
    "depends": ["pos_notification", "point_of_sale"],
    "data": [
        "security/ir.model.access.csv",
        "views/assets.xml",
        "views/pos_config_views.xml",
        "views/pos_service_views.xml",
    ],
    "qweb": [
        "static/src/xml/*.xml",
    ],
    "auto_install": False,
    "installable": True,
}
