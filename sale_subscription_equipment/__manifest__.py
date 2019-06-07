# -*- coding: utf-8 -*-

{
    'name': 'Subscriptions of Equipments',
    'version': '1.0',
    'category': 'Sales',
    'description': """
This module allows you to set a deferred revenue on your subscriptions.
""",
    'depends': ['sale_subscription', 'equipment'],
    'data': [
        'views/sale_subscription_views.xml',
        'security/ir.model.access.csv'
    ],
    'installable': True,
    'auto_install': True,
}
