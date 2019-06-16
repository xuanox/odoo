# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Equipment - Helpdesk',
    'version': '1.1',
    'category': 'Equipment',
    'summary': 'Schedule and manage maintenance on machine and tools.',
    'website': 'https://www.odoo.com/page/tpm-maintenance-software',
    'description': """
Equipment in Helpdesk
==================
* Preventive vs corrective maintenance
* Define different stages for your maintenance requests
* Plan maintenance requests (also recurring preventive)
* Equipments related to workcenters
* MTBF, MTTR, ...
""",
    'depends': ['equipment', 'helpdesk', 'helpdesk_technical_support'],
    'data': [
         'views/equipment_views.xml',
        'views/helpdesk_views.xml',
        'data/maintenance_cron.xml',
    ],
    'demo': [],
    'auto_install': True,
}
