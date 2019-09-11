# -*- coding: utf-8 -*-
###################################################################################
#
#    Electrónica Médica.
#    Copyright (C) 2019-TODAY Electrónica Médica (<https://www.electronicamedica.com>).
#
#    Author: Rocendo Tejada (<https://www.electronicamedica.com>)
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

from datetime import date, datetime, timedelta
from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError

class RegulatoryTechnicalCriteria(models.Model):
    _name = 'regulatory.technical.criteria'
    _description = 'Regulatory Technical Criteria'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    STATE_SELECTION = [
        ('valid', 'Valid'),
        ('stamp_to_expire', 'Stamp to Expire'),
        ('expired_stamp', 'Expired Stamp'),
        ('tc_to_expire', 'TC to Expire'),
        ('expired_tc', 'Expired TC')
    ]

    name = fields.Char(string="Certificate Name", required=True, translate=True, track_visibility='onchange')
    ctni=fields.Char('CTNI', track_visibility='onchange')
    technical_file=fields.Char('Certificate Number', track_visibility='onchange')
    criterion_expiration_date = fields.Date(u'Criterion Expiration Date', track_visibility='onchange')
    date_expiration_authenticated_seal = fields.Date(u'Date Expiration of the Authenticated Seal', track_visibility='onchange')
    description=fields.Text('Description', track_visibility='onchange')
    qty_available = fields.Integer('Quantity Available', default=0, help="Assign Quantity Available.", track_visibility='onchange')
    minimum_quantity = fields.Integer('Minimum Quantity', default=0, help="Assign Minimum Quantity.", track_visibility='onchange')
    state = fields.Selection(STATE_SELECTION, 'Status', readonly=True, track_visibility='onchange',
        help="When the maintenance order is created the status is set to 'New'.\n\
        If the TC is Valid the status is set to 'Valid'.\n\
        If the TC is Stamp to Expire the status is set to 'Stamp to Expire'.\n\
        If the TC is Expired Stamp the status is set to 'Expired Stamp'.\n\
        If the TC is Technical Criteria to Expire then the status is set to 'TC to Expire'.\n\
        If the TC is Expired Technical Criteria, the status is set to 'Expired TC'.", default='valid')
    is_minimum_quantity = fields.Boolean('Minimum Quantity', track_visibility=True)
    is_unavailable = fields.Boolean('Unavailable', track_visibility=True)

    @api.onchange('qty_available', 'minimum_quantity')
    def onchange_qty_available(self):
        minimum = self.minimum_quantity
        available = self.qty_available
        if available =< minimum:
            self.is_minimum_quantity = True
        if available == 0:
            self.is_unavailable = True
        return True
