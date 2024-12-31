{
    "name": "POS later payment stages",
    "version": "14.0.0.0.0",
    "category": "Point of Sale",
    "author": "Eng. Fares",
    "license": "AGPL-3",
    "depends": ["pos_pay_later"],
    "data": [
        "security/ir.model.access.csv",
        "data/service_stage_data.xml",
        "views/assets.xml",
        "views/pos_service_views.xml",
        "views/pos_session.xml",
        "views/service_stage_views.xml",
    ],
    "qweb": [
        "static/src/xml/*.xml",
    ],
    "auto_install": False,
    "installable": True,
}
