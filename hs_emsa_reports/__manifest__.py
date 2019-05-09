# -*- coding: utf-8 -*-
{
	'name': 'hs_emsa_reports',

	'summary': 'Reportes Personalizados',

	'description': """
		Conjunto de Reportes personalizados para la empresa Electronica Medica S.A.
	""",

	'author': 'HS Consulting S.A.',
	'website': 'http://www.hconsul.com/odoo/',
	'maintainer': 'Luis Dominguez',
	
	# Categories can be used to filter modules in modules listing
	# Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
	# for the full list
	'category': 'Invoicing &amp; Payments',
	'license': 'LGPL-3',
	'version': '0.57',
	
	# any module necessary for this one to work correctly
	'depends': ['base', 'account', 'account_reports'],
	
	# always loaded
	'data': [
		'views/products.xml',
		'views/ledger_report.xml',
		'views/vendor_bills.xml',
	],
	
	'installable': True,
	'auto_install': True,
	'application': False,
}
