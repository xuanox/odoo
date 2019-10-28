# -*- coding: utf-8 -*-
{
	'name': "hs_account_extra",

	'summary': """
		Configuraciones extra a accounting """,

	'description': """
		Configuraciones personalizadas al modulo de contibilidad
	""",

	'author': "HS Consulting S.A.",
	'website': "http://www.hconsul.com/odoo/",

	# Categories can be used to filter modules in modules listing
	# Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
	# for the full list
	'category': 'other',
	'version': '0.3',

	# any module necessary for this one to work correctly
	'depends': ['base', 'account'],

	# always loaded
	'data': [
		# 'security/ir.model.access.csv',
		'security/account_invoice_groups.xml'
		'views/account_invoice.xml',
	],

	# only loaded in demonstration mode
	'demo': [
		#'demo/demo.xml',
	],
}