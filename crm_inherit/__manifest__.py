# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "CRM Inherit",
    'version': "1.0",
    'category': "Sales",
    'summary': "Advanced features for CRM",
    'description': """
Contains advanced features for CRM such as new views
    """,
    'depends': ['crm', 'equipment'],
    'data': [
        'views/equipment_views.xml',
        'views/crm_category_views.xml',
        'views/crm_team_views.xml',
        'views/crm_lead_views.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
}
