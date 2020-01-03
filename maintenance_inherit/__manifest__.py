# -*- coding: utf-8 -*-

{
    'name': 'Maintenance Inherit',
    'version': '1.0',
    'sequence': 125,
    'category': 'IT',
    'description': """
        Track equipments and maintenance requests""",
    'depends': ['maintenance'],
    'summary': 'Track equipment and manage maintenance requests',
    'website': 'https://www.odoo.com/page/tpm-maintenance-software',
    'data': [
        'security/ir.model.access.csv',
        'views/maintenance_views.xml'
    ],
    'installable': True,
    'application': True,
}
