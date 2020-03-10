# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'CRM - Tender',
    'version': '1.1',
    "author": "Electronica Médica",
    'category': 'Hidden',
    'description': """
This module adds a shortcut the CRM in Tenders.
===========================================================================

This shortcut allows you to generate a Tenders in CRM.

    """,
    'depends': ['crm', 'regulatory_issue', 'equipment', 'product'],
    'data': [
        'security/ir.model.access.csv',    
        'views/crm_views.xml',
    ],
    'auto_install': True,
}
