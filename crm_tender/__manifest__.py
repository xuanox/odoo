# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'CRM to Tender',
    'version': '1.4',
    "author": "Rocendo Tejada - Electronica Médica",
    'category': 'Hidden',
    'description': """
This module adds a shortcut the CRM in Tender.
===========================================================================

This shortcut allows you to generate a Crm Tender.

    """,
    'depends': ['crm'],
    'data': [
        'views/crm_lead_views.xml'
    ],
    'auto_install': True,
}
