# -*- coding: utf-8 -*-

{
    'name': 'Subscriptions of Equipments',
    'version': '1.0',
    'category': 'Sales',
    'description': """
This module allows you to set a deferred revenue on your subscriptions.
""",
    'depends': ['sale_subscription', 'equipment', 'helpdesk', 'helpdesk_technical_support'],
    'data': [
        'security/ir.model.access.csv'
        'views/sale_subscription_views.xml',
        'views/equipment_views.xml',
        'views/helpdesk_views.xml',
        'views/technical_support_views.xml',
    ],
    'installable': True,
    'auto_install': True,
}
