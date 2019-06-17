# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Margins in Parts Orders',
    'version':'1.0',
    'category': 'Parts',
    'description': """
This module adds the 'Margin' on parts order.
=============================================

This gives the profitability by calculating the difference between the Unit
Price and Cost Price.
    """,
    'depends':['part'],
    'data':[
    #'security/ir.model.access.csv',
    #'views/part_margin_view.xml'
    ],
}
