# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Part To Purchase',
    'summary': 'Part based on service outsourcing.',
    'description': """
Allows the outsourcing of services. This module allows one to sell services provided
by external providers and will automatically generate purchase orders directed to the service seller.
    """,
    'version': '1.0',
    'website': 'https://www.odoo.com/',
    'category': 'Hidden',
    'depends': [
        'part',
        'purchase',
        'technical_support',
        'equipment',
        'part_stock_picking'
    ],
    'data': [
        'views/part_views.xml',
        'views/purchase_views.xml',
    ],
    'demo': [
    ],
    'auto_install': True,
}
