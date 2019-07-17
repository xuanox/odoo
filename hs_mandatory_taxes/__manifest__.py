# -*- coding: utf-8 -*-
{
	'name': "hs_mandatory_taxes",

	'summary': """
		Impuestos Obligatorios""",

	'description': """
		Este modulo obliga que los campos 
	""",

	'author': "HS Consulting S.A.",
	'website': "http://www.hconsul.com/odoo/",

	# Categories can be used to filter modules in modules listing
	# Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
	# for the full list
	'category': 'Sales',
	'version': '0.7',

	# any module necessary for this one to work correctly
	'depends': ['base', 'account', 'purchase', 'sale'],

	# always loaded
	'data': [
		# 'security/ir.model.access.csv',
		'views/taxes.xml'
	],
	
	'installable': True,
	'auto_install': True,
	'application': False,
}