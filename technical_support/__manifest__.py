# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo
#    Copyright (C) 2013-2018 emsa (<http://www.electronicamedica.com>).
#
##############################################################################

{
    'name': 'Technical Support',
    'version': '1.3',
    'summary': 'Equipment Maintenance, Diagnostic, Preventive, Corrective, Repair and Operation',
    'description': """
Manage Maintenance process in Odoo
=====================================

Equipment Maintenance, Diagnostic, Repair and Operation.
Support Breakdown Maintenance and Corrective Maintenance.

Main Features
-------------
    * Request Service/Maintenance Management
    * Maintenance Orders Management
    * Work Orders Management (group MO)
    * Parts Management
    * Tasks Management (standard job)
    * Convert Maintenance Order to Task
    * Print Maintenance Order
    * Print Maintenance Request

Required modules:
    * equipment
    """,
    'author': 'emsa',
    'website': 'http://www.electronicamedica.com',
    'category': 'Productivity',
    'sequence': 0,
    'depends': ['asset','equipment','purchase','helpdesk', 'part'],
    'demo': ['data/technical_support_demo.xml'],
    'data': [
        'security/technical_support_security.xml',
        'security/ir.model.access.csv',
        'wizard/reject_view.xml',
        'wizard/convert_order.xml',
        'data/technical_support_sequence.xml',
        'data/technical_support_data.xml',
        'data/mail_template_data.xml',
        'views/technical_support_view.xml',
        'views/technical_support_order_view.xml',
        'views/equipment_view.xml',
        'views/product_view.xml',
        'views/technical_support_workorder_view.xml',
        'report/report_technical_support_order.xml',
        'report/report_technical_support_request.xml',
        'report/technical_support_report.xml',
        'report/report_technical_support_templates.xml',
    ],
    'application': True,
}
