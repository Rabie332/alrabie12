{
    "name": "Pos Extra products",
    "version": "14.0.1.0.1",
    "category": "POS",
    "author": "Hadooc",
    "depends": ["point_of_sale", "pos_restaurant"],
    "data": [
        "security/ir.model.access.csv",
        "views/assets.xml",
        "views/pos_notes_views.xml",
        "views/product_template_views.xml",
        "views/view_pos_config.xml",
    ],
    "qweb": [
        "static/src/xml/*.xml",
    ],
    "installable": True,
    "license": "AGPL-3",
}
