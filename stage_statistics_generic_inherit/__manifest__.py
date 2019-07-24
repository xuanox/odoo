# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Generic: Stage Statistics Inherit',
    'version': '1.0',
    'category': 'Productivity',
    'sequence': 5,
    'summary': 'Track Technical Support and Equipment',
    'description': "",
    'depends': [
        'technical_support',
        'part',
        'regulatory_issue',
    ],
    'data': [
        'views/technical_support_views.xml',
        'views/regulatory_issue_views.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
}
