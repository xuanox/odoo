# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo
#    Copyright (C) 2018-2019 emsa (<http://www.electronicamedica.com>).
#
##############################################################################

{
    'name': 'Equipment',
    'version': '1.3',
    'summary': 'Equipment Management',
    'description': """
Managing Equipment in Odoo.
===========================
Support following feature:
    * Location for Equipment
    * Assign Equipment to Client
    * Track warranty information
    * Custom states of Equipment
    * States of Equipment for different team: Finance, Warehouse, Manufacture, Maintenance and Accounting
    * Drag&Drop manage states of Equipment
    * Equipment Tags
    * Search by main fields
    """,
    'author': 'Rocendo Tejada',
    'website': 'http://www.electronicamedica.com',
    'category': 'Industries',
    'sequence': 0,
    'depends': ['stock', 'helpdesk', 'asset'],
    'demo': ['data/equipment_demo.xml'],
    'data': [
        'security/equipment_security.xml',
        'security/ir.model.access.csv',
        'data/equipment_data.xml',
        'data/stock_data.xml',
        'data/equipment_sequence.xml',
        'views/equipment_view.xml',
        'views/equipment_brand_view.xml',
        'views/equipment_zone_view.xml',
        'views/equipment_model_view.xml',
        'views/equipment_software_view.xml',
        'views/equipment_dicom_view.xml',
        'views/equipment_network_view.xml',
        'views/equipment_modality_view.xml',
        'views/equipment.xml',
    ],
    'installable': True,
    'application': True,
}
