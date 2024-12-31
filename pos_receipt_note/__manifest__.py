{
    "name": "Notes in POS receipt",
    "version": "14.0.1.0.1",
    "summary": """
      Add notes in POS receipt
       """,
    "category": "Point of Sale",
    "author": "Odox SoftHub, Hadooc",
    "website": "https://www.odoxsofthub.com",
    "depends": ["pos_restaurant"],
    "data": [
        "views/assets.xml",
        "views/pos_order_views.xml",
        "views/pos_config_views.xml",
    ],
    "qweb": ["static/src/xml/ReceiptScreen.xml"],
    "images": ["static/description/thumbnail.gif"],
    "license": "LGPL-3",
    "installable": True,
    "application": True,
}
