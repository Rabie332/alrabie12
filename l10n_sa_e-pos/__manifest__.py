# -*- coding: utf-8 -*-

{
    "name": "Saudi Arabia POS e-invoice Phase 2 (Integration Phase)",
    "version": "14.0.1.1.1",
    "category": "Accounting/Localizations/Point of Sale",
    "license": "OPL-1",
    "summary": "POS electronic invoice for Saudi Arabia distribution according to ZATCA requirements",
    "price": 120.0,
    "currency": "USD",
    "author": "HMPRO",
    "website": "",
    "depends": ["point_of_sale", "l10n_sa_e-invoice", "l10n_sa_pos"],
    "data": [
        "views/assets.xml",
        "data/data.xml",
        # "views/pos.xml",
    ],
    "installable": True,
    "images": ["static/description/banner.png"],
    "qweb": ["static/src/xml/pos.xml"],
}
