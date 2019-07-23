# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Helpdesk to Technical Support',
    'version': '1.0',
    "author": "Rocendo Tejada - Electronica Médica",
    'category': 'Hidden',
    'description': """
This module adds a shortcut the Technical Support in Helpdesk.
===========================================================================

This shortcut allows you to generate a Technical Support Order.

    """,
    'depends': ['helpdesk', 'technical_support', 'equipment'],
    'data': [
        'data/mail_data.xml',
        'wizard/pending_view.xml',
        'wizard/cause_view.xml',
        'wizard/assign_view.xml',
        'wizard/equipment_view.xml',
        #'wizard/schedule_view.xml',
        'security/ir.model.access.csv',
        'views/technical_support_views.xml',
        'views/helpdesk_technical_support_templates.xml',
        'views/helpdesk_views.xml',
        'views/equipment_views.xml',
        'views/res_config_settings_views.xml',
        'views/res_partner_views.xml',
    ],
    'auto_install': True,
}
