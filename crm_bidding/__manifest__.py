# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'CRM - Bidding',
    'version': '1.1',
    "author": "Rocendo Tejada - Electronica Médica",
    'category': 'Hidden',
    'description': """
This module adds a shortcut the CRM in Bidding.
===========================================================================

This shortcut allows you to generate a Bidding in CRM.

    """,
    'depends': ['crm', 'regulatory_issue', 'equipment'],
    'data': [
        'security/ir.model.access.csv',    
        'views/crm_views.xml',
    ],
    'auto_install': True,
}
