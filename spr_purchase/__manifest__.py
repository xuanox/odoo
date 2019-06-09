# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'SPR - Purchase',
    'summary': 'SPR - Purchase.',
    'description': """
Allows the outsourcing of services. This module allows one to sell services provided
by external providers and will automatically generate purchase orders directed to the service seller.
    """,
    'version': '1.0',
    'category': 'Hidden',
    'depends': [
        'part',
        'purchase',
    ],
    'data': [
        #'data/mail_data.xml',
        #'views/product_views.xml',
        #'views/part_views.xml',
    ],
    'demo': [
    ],
    'auto_install': True,
}
