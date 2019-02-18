# -*- coding: utf-8 -*-
{
    'name': "PA Check Layout for Odoo 12",

    'summary': """
        Impresión de cheques para Panamá
    """,

    'description': """
        Este es un módulo para la impresión de cheques en territorio de Panamá, 
        requiere configurar la plantilla de impresión de acuerdo al cliente.

        Este modulo es unicamente compatible con Odoo 12.
    """,

    'author': "HS Consulting S.A.",
    'website': "http://www.hconsul.com/odoo/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Localization',
    'version': '0.3',

    # any module necessary for this one to work correctly
    'depends': ['account_check_printing', 'hr_expense_check', 'l10n_pa'],

    # always loaded
    'data': [
		'views/action_print_check.xml',
		'views/print_check.xml',
		'views/print_check_pa.xml',
    ],
    'installable': True,
    'auto_install': True,
    'license': 'OEEL-1',
}