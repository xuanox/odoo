# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Spare Parts Management',
    'version': '1.0',
    'sequence': 200,
    'category': 'Productivity',
    'summary': 'Spare Parts Management',
    'description': """
El objetivo es tener un módulo completo para gestionar todas las piezas del equipo.
====================================================================

Los siguientes temas están cubiertos por este módulo:
------------------------------------------------------
    * Add/remove parts
    * Impact for stocks
    * Invoicing (products and/or services)
    * Warranty concept
    * Part quotation report
    * Notes for the technician and for the final customer
""",
    'depends': ['stock', 'sale_management', 'account', 'equipment'],
    'data': [
        'security/ir.model.access.csv',
        'security/part_security.xml',
        'wizard/part_cancel_views.xml',
        'wizard/part_make_invoice_views.xml',
        'wizard/stock_warn_insufficient_qty_views.xml',
        'views/part_views.xml',
        'report/part_reports.xml',
        'report/part_templates_part_order.xml',
        'data/ir_sequence_data.xml',
        'data/part_data.xml',
    ],
    'demo': ['data/part_demo.xml'],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
