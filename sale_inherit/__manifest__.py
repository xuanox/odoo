# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "Sale Inherit",
    'version': "1.0",
    'category': "Sales",
    'summary': "Advanced Features for Sale Management",
    'description': """
Contains advanced features for sale management
    """,
    'depends': ['sale'],
    'data': [
        'views/sale_views.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
}
