# -*- coding: utf-8 -*-
###################################################################################
#
#    Electrónica Médica by Aldhair Atencio
#    Copyright (C) 2019-TODAY Electrónica Médica (<https://www.electronicamedica.com>).
#
#    Author: Aldhair Atencio
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
    'name': 'continuing education',
    'summary': """continuing education""",
    'version': '12.0.1.0.0',
    'author': 'Aldhair Atencio',
    'website': "http://www.electronicamedica.com",
    'company': 'Electrónica Médica',
    "category": "Productivity",
    'icon': '/continuing_education/static/src/img/icon.png',
    'depends': ['base', 'calendar', 'mail'],
    'data': [

            'security/continuing_education.xml',
            'security/ir.model.access.csv',
            'wizard/assign_view.xml',
            'data/continuing_education_sequence.xml',
            'views/continuing_education_templates.xml',
            'views/continuing_education_dashboard_views.xml',
            'views/continuing_education_views.xml',


    ],
    'demo': [],
    'images': [
        'static/description/banner.jpg'
    ],
    'license': 'AGPL-3',
    'installable': True,
    'application': True,
}
