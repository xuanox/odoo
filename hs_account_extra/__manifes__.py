# -*- coding: utf-8 -*-
{
	'name': "hs_emsa_account",

	'summary': """
		Configuraciones extra a accounting """,

	'description': """
		Configuraciones personalizadas al modulo de contibilidad
	""",

	'author': 'HS Consulting S.A.',
	'website': 'http://www.hconsul.com/odoo/',
	'maintainer': 'Luis Dominguez',

	# Categories can be used to filter modules in modules listing
	# Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
	# for the full list
	'category': 'Invoicing & Payments',
	'license': 'LGPL-3',
	'version': '1.00',

	# any module necessary for this one to work correctly
	'depends': ['base', 'account'],

	# always loaded
	'data': [
		'security/account_invoice_groups.xml'
		'views/account_invoice_view.xml',
	],

	'installable': True,
	'auto_install': True,
}