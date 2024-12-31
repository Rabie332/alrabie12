{
    'name': 'Custom Survey Link',
    'version': '14.0.1.0.0',
    'summary': 'Link survey responses to partner records',
    'category': 'Tools',
    'author': 'Eng. Fares',
    'depends': ['survey', 'contacts', 'crm'],
    'data': [
        "views/survey_view.xml",
        "views/crm_lead_view.xml",
    ],
    'installable': True,
    'auto_install': False,
}
