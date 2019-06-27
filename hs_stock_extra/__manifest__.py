# -*- coding: utf-8 -*-
{
	'name': "hs_stock_extra",

	'summary': """
		Modificaciones a inventario """,

	'description': """
		Realiza modificaciones al sistema de inventario en la empresa EMSA.
		- 
	""",

	'author': "HS Consulting S.A.",
	'website': "http://www.hconsul.com/odoo/",

	# Categories can be used to filter modules in modules listing
	# Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
	# for the full list
	'category': 'other',
	'version': '0.5',

	# any module necessary for this one to work correctly
	'depends': ['base', 'stock'],

	# always loaded
	'data': [
		# 'security/ir.model.access.csv',
		'views/stock.xml',
	],

	# only loaded in demonstration mode
	'demo': [
		#'demo/demo.xml',
	],
	
	'installable': True,
	'auto_install': True,
	'application': False,
}