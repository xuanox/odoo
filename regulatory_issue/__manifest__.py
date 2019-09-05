# -*- coding: utf-8 -*-
###################################################################################
#
#    Electrónica Médica by Rocendo Tejada
#    Copyright (C) 2019-TODAY Electrónica Médica (<https://www.electronicamedica.com>).
#
#    Author: Rocendo Tejada
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###################################################################################
{
    'name': 'Regulatory Issue Management',
    'summary': """Regulatory Issue Management""",
    'version': '12.0.1.1.9',
    'author': 'Rocendo Tejada',
    'website': "http://www.electronicamedica.com",
    'company': 'Electrónica Médica',
    "category": "Productivity",
    'icon': '/regulatory_issue/static/src/img/icon.png',
    'depends': ['base', 'calendar', 'mail', 'equipment'],
    'data': [
        'security/regulatory_issue.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'data/mail_template_data.xml',
        'data/mail_data.xml',
        'wizard/assign_view.xml',
        'wizard/appointment_view.xml',
        'wizard/registry_lost_views.xml',
        'wizard/reject_view.xml',
        'wizard/homologation_view.xml',
        'views/regulatory_templates.xml',
        'views/regulatory_license_views.xml',
        'views/regulatory_legal_documentation_views.xml',
        'views/regulatory_technical_criteria_views.xml',
        'views/regulatory_technical_file_views.xml',
        'views/regulatory_technical_file_creation_views.xml',
        'views/regulatory_technical_file_modification_views.xml',
        'views/regulatory_technical_file_registry_views.xml',
        'views/regulatory_dashboard_views.xml',
        'views/regulatory_views.xml',
    ],
    'demo': [],
    'images': ['static/description/banner.jpg'],
    'license': 'AGPL-3',
    'installable': True,
    'application': True,
}
