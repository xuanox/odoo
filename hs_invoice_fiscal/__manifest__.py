# -*- coding: utf-8 -*-
{
	'name': "hs_invoice_fiscal",

	'summary': """
		Facturacion en impresora fiscal """,

	'description': """
		Permite la conexion de facturas con impresoras fiscales.
	""",

	'author': "Hermec Solutions S.A.",
	'website': "http://www.hermecsolutions.com/",

	# Categories can be used to filter modules in modules listing
	# Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
	# for the full list
	'category': 'report',
	'version': '0.27',

	# any module necessary for this one to work correctly
	'depends': ['base', 'account'],

	# always loaded
	'data': [
		# 'security/ir.model.access.csv',
		'views/views.xml',
		'views/templates.xml',
	],
	# only loaded in demonstration mode
	'demo': [
		'demo/demo.xml',
	],
}