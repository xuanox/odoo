# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Helpdesk to Spare Part Request',
    'version': '1.4',
    "author": "Rocendo Tejada - Electronica Médica",
    'category': 'Hidden',
    'description': """
This module adds a shortcut the Spare Part Request in Helpdesk.
===========================================================================

This shortcut allows you to generate a Spare Part Request.

    """,
    'depends': ['helpdesk', 'technical_support', 'equipment', 'part'],
    'data': [
        #'wizard/spare_part_request_view.xml',
        #'wizard/incorrect_part_number_view.xml',
        'views/part_views.xml',
        'views/helpdesk_views.xml',
        'views/technical_support_order_views.xml',
    ],
    'auto_install': True,
}
