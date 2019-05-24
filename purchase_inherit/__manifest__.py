# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Purchase Inherit',
    'summary': 'Part based on service outsourcing.',
    'description': """
Allows the outsourcing of services. This module allows one to sell services provided
by external providers and will automatically generate purchase orders directed to the service seller.
    """,
    'version': '1.0',
    'website': 'https://www.odoo.com/',
    'category': 'Hidden',
    'depends': [
        'purchase'
    ],
    'data': [
        'views/purchase_views.xml',
    ],
    'demo': [
    ],
    'auto_install': True,
}
