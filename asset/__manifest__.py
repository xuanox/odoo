# -*- coding: utf-8 -*-

{
    'name': 'Assets',
    'version': '12.0',
    'summary': 'Asset Management',
    'description': """Managing Assets in Odoo""",
    'author': 'Rocendo Tejada',
    'website': 'http://electronicamedica.com',
    'category': 'Assets',
    'sequence': 11,
    'depends': ['stock'],
    'demo': [],
    'data': [
        'security/asset_security.xml',
        'security/ir.model.access.csv',
        'data/asset_data.xml',
        'data/stock_data.xml',
        'views/asset_view.xml',
        'views/asset.xml',
    ],
    'installable': True,
    'application': True,
}
