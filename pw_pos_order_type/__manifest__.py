{
    "name": "PoS Order Types",
    "category": "Point of Sale",
    "summary": "This apps helps you to set order type for pos order "
    "from pos interface | POS Order Type in Odoo",
    "author": "Preway IT Solutions, Hadooc",
    "license": "AGPL-3",
    "version": "14.0.1.0.0",
    "depends": ["point_of_sale"],
    "data": [
        "security/ir.model.access.csv",
        "views/views.xml",
        "views/pos_order_type_view.xml",
    ],
    "price": 10.0,
    "currency": "EUR",
    "qweb": ["static/src/xml/pos.xml"],
    "installable": True,
    "auto_install": False,
    "images": ["static/description/Banner.png"],
}
