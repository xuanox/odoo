# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Generic: Stage Statistics',
    'version': '1.0',
    'category': 'Sales',
    'sequence': 5,
    'summary': 'Track leads and close opportunities',
    'description': "",
    'depends': [
        'crm',
        'helpdesk',
        'hr_recruitment',
        'project',
        'purchase',
        'quality_control',
        'sale_management',
        'stock',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/crm_lead_views.xml',
        'views/helpdesk_ticket_views.xml',
        'views/hr_applicant_views.xml',
        'views/project_task_views.xml',
        'views/purchase_order_views.xml',
        'views/quality_check_views.xml',
        'views/sale_order_views.xml',
        'views/stock_picking_views.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
}

