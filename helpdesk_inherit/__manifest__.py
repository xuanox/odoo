# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Helpdesk Inherit',
    'version': '1.0',
    "author": "Rocendo Tejada - Electronica Médica",
    'category': 'Hidden',
    'description': '',
    'depends': ['helpdesk'],
    'data': [
        'data/mail_data.xml',
        'wizard/reasign_ticket_view.xml',
        'views/helpdesk_views.xml',        
    ],
    'auto_install': True,
}
