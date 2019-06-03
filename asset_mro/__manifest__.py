# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Asset - Mro',
    'version': '1.1',
    'category': 'Asset',
    'summary': 'Schedule and manage maintenance on machine and tools.',
    'website': 'https://www.odoo.com/page/tpm-maintenance-software',
    'description': """
Asset in Mro
==================
* Preventive vs corrective maintenance
* Define different stages for your maintenance requests
* Plan maintenance requests (also recurring preventive)
* Equipments related to workcenters
* MTBF, MTTR, ...
""",
    'depends': ['asset', 'mro'],
    'data': [
        'views/asset_views.xml',
        'views/mro_views.xml',
        'data/maintenance_cron.xml',
    ],
    'demo': [],
    'auto_install': True,
}
