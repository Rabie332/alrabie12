{
    'name': 'Loan Management',
    'version': '1.0',
    'author': 'Eng. Fares',
    'category': 'Finance',
    'summary': 'Manage bank loans for the company',
    'description':  """
                    Manage bank loans for the company.
                    """,
    'depends': ['account'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/loan_views.xml',
        'views/payment_views.xml',
    ],
    'installable': True,
    'auto_install': False,
}
