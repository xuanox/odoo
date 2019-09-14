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
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError

class RegulatoryTechnicalCriteria(models.Model):
    _name = 'regulatory.technical.criteria'
    _description = 'Regulatory Technical Criteria'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name asc'

    STATE_SELECTION = [
        ('valid', 'Valid'),
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
    max_quantity = fields.Integer('Max Quantity', default=0, help="Assign Max Quantity.", track_visibility='onchange')
    state = fields.Selection(STATE_SELECTION, 'Status', readonly=True, track_visibility='onchange',
        help="When the maintenance order is created the status is set to 'New'.\n\
        If the TC is Valid the status is set to 'Valid'.\n\
        If the TC is Technical Criteria to Expire then the status is set to 'TC to Expire'.\n\
        If the TC is Expired Technical Criteria, the status is set to 'Expired TC'.", default='valid')
    is_minimum_quantity = fields.Boolean('Check Minimum Quantity', track_visibility=True)
    is_unavailable = fields.Boolean('Unavailable', track_visibility=True)
    is_stamp_to_expire = fields.Boolean('Stamp to Expire', track_visibility=True)
    is_expired_stamp = fields.Boolean('Expired Stamp', track_visibility=True)

    def set_stamp_to_expire(self):
        return self.write({'is_stamp_to_expire': True})

    def set_expired_stamp(self):
        return self.write({'is_expired_stamp': True})

    def set_tc_to_expire(self):
        return self.write({'state': 'tc_to_expire'})

    def set_expired_tc(self):
        return self.write({'state': 'expired_tc'})

    @api.model
    def _cron_change_state_tc(self):
        today = fields.Date.today()
        next_month = fields.Date.to_string(fields.Date.from_string(today) + relativedelta(months=1))

        # set to pending if date is in less than a month
        domain_pending = [('criterion_expiration_date', '<', next_month), ('state', '=', 'valid')]
        subscriptions_pending = self.search(domain_pending)
        subscriptions_pending.set_tc_to_expire()

        # set to close if date is passed
        domain_close = [('criterion_expiration_date', '<', today), ('state', '=', 'tc_to_expire')]
        subscriptions_close = self.search(domain_close)
        subscriptions_close.set_expired_tc()

        return dict(pending=subscriptions_pending.ids, closed=subscriptions_close.ids)

    @api.model
    def _cron_change_state_tc_stamp(self):
        today = fields.Date.today()
        next_month = fields.Date.to_string(fields.Date.from_string(today) + relativedelta(months=1))

        # set to pending if date is in less than a month
        domain_pending = [('date_expiration_authenticated_seal', '<', next_month), ('is_stamp_to_expire', '=', False)]
        subscriptions_pending = self.search(domain_pending)
        subscriptions_pending.set_stamp_to_expire()

        # set to close if date is passed
        domain_close = [('date_expiration_authenticated_seal', '<', today), ('is_expired_stamp', '=', False)]
        subscriptions_close = self.search(domain_close)
        subscriptions_close.set_expired_stamp()

        return dict(pending=subscriptions_pending.ids, closed=subscriptions_close.ids)
