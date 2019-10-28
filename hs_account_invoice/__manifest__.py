# -*- coding: utf-8 -*-
{
	'name': "hs_account_invoice",

	'summary': """
		Modificaciones a facturacion """,

	'description': """
		Realiza modificaciones al sistema de facturacion en la empresa EMSA.
		- Agrega la columna 'Tipo de Factura' a Invoice/Credit Note
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
		'views/account_invoice.xml',
	],

	# only loaded in demonstration mode
	'demo': [
		#'demo/demo.xml',
	],

	'installable': True,
	'auto_install': True,
}