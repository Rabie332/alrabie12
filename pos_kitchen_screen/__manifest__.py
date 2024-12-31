{
    "name": "POS Kitchen screen",
    "version": "14.0.1.0.0",
    "category": "Sales/Point of Sale",
    "author": "Hadooc",
    "license": "AGPL-3",
    "depends": ["pos_restaurant", "web_one2many_kanban"],
    "data": [
        "security/ir.model.access.csv",
        "data/kitchen_stage_data.xml",
        "views/assets.xml",
        "views/pos_order_views.xml",
        "views/pos_session.xml",
        "views/kitchen_stage_views.xml",
    ],
    "qweb": ["static/src/xml/*.xml"],
    "installable": True,
}
