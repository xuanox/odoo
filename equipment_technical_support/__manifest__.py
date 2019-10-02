# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo
#    Copyright (C) 2013-2018 emsa (<http://www.electronicamedica.com>).
#
##############################################################################

{
    'name': 'Equipment - Technical Support',
    'version': '1.1',
    'category': 'equipment',
    'summary': 'Schedule and manage maintenance on machine and tools.',
    'website': 'https://www.odoo.com/page/tpm-maintenance-software',
    'description': """
Equipment in Technical Support
==================
* Preventive vs corrective maintenance
* Define different stages for your maintenance requests
* Plan maintenance requests (also recurring preventive)
* Equipments related to workcenters
* MTBF, MTTR, ...
""",
    'depends': ['equipment', 'technical_support'],
    'data': [
        #'views/equipment_views.xml',
        #'views/technical_support_views.xml',
        #'data/maintenance_cron.xml',
    ],
    'demo': [],
    'auto_install': True,
}
