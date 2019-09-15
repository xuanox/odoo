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
    criterion_expiration_date = fields.Date(string='Criterion Expiration Date', track_visibility='onchange')
    date_expiration_authenticated_seal = fields.Date(string='Date Expiration Stamp', track_visibility='onchange')
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

    def set_is_minimum_quantity(self):
        return self.write({'is_minimum_quantity': True})

    def set_is_minimum_quantity_false(self):
        return self.write({'is_minimum_quantity': False})

    def set_is_unavailable(self):
        return self.write({'is_unavailable': True})

    def set_is_unavailable_false(self):
        return self.write({'is_unavailable': False})

    def set_stamp_to_expire(self):
        return self.write({'is_stamp_to_expire': True})

    def set_stamp_to_expire_false(self):
        return self.write({'is_stamp_to_expire': False})

    def set_expired_stamp(self):
        return self.write({'is_expired_stamp': True})

    def set_expired_stamp_false(self):
        return self.write({'is_expired_stamp': False})

    def set_to_valid(self):
        return self.write({'state': 'valid'})

    def set_tc_to_expire(self):
        return self.write({'state': 'tc_to_expire'})

    def set_expired_tc(self):
        return self.write({'state': 'expired_tc'})

    @api.multi
    def check_status(self):
        if self.state == 'valid':
            self._cron_change_state_tc()
        if self.state == 'tc_to_expire' or self.state == 'expired_tc':
            self.change_state_valid_tc()
            self._cron_change_state_tc()
        return super(RegulatoryTechnicalCriteria, self)

    @api.multi
    def check_expiration_stamp(self):
        if self.is_stamp_to_expire == False or self.is_expired_stamp == False:
            self._cron_change_state_tc_stamp()
        if self.is_stamp_to_expire == True or self.is_expired_stamp == True:
            self.change_expiration_tc_stamp()
            self._cron_change_state_tc_stamp()
        return super(RegulatoryTechnicalCriteria, self)

    @api.multi
    def write(self, vals):
        res = super(RegulatoryTechnicalCriteria, self).write(vals)
        if vals.get('criterion_expiration_date'):
            self.check_status()
        if vals.get('date_expiration_authenticated_seal'):
            self.check_expiration_stamp()
        return res

    @api.model
    def _cron_change_state_tc(self):
        today = fields.Date.today()
        next_month = fields.Date.to_string(fields.Date.from_string(today) + relativedelta(months=1))

        # set to expiration tc if date is in less than a month
        domain_expiration = [('criterion_expiration_date', '<', next_month),  '|', ('state', '=', 'expired_tc'), ('state', '=', 'valid')]
        tc_expired = self.search(domain_expiration)
        tc_expired.set_tc_to_expire()

        # set to expiration tc if date is passed
        domain_expired = [('criterion_expiration_date', '<', today), '|', ('state', '=', 'tc_to_expire'), ('state', '=', 'valid')]
        expired_tc = self.search(domain_expired)
        expired_tc.set_expired_tc()

        return dict(expiration_tc=tc_expired.ids, expired_tc=expired_tc.ids)

    @api.model
    def change_state_valid_tc(self):
        today = fields.Date.today()
        next_month = fields.Date.to_string(fields.Date.from_string(today) + relativedelta(months=1))

        # set to expiration tc if date is in less than a month
        domain_valid = [('criterion_expiration_date', '>', next_month), '|', ('state', '=', 'tc_to_expire'), ('state', '=', 'expired_tc')]
        tc_valid = self.search(domain_valid)
        tc_valid.set_to_valid()

        return dict(valid_tc=tc_valid.ids)

    @api.model
    def _cron_change_state_tc_stamp(self):
        today = fields.Date.today()
        next_month = fields.Date.to_string(fields.Date.from_string(today) + relativedelta(months=1))

        # set to expiration if date is in less than a month
        domain_expiration_stamp = [('date_expiration_authenticated_seal', '<', next_month), '|', ('is_stamp_to_expire', '=', False), ('is_expired_stamp', '=', True)]
        tc_stamp_expired = self.search(domain_expiration_stamp)
        tc_stamp_expired.set_stamp_to_expire()

        # set to expired if date is passed
        domain_expired_stamp = [('date_expiration_authenticated_seal', '<', today), '|', ('is_stamp_to_expire', '=', True), ('is_expired_stamp', '=', False)]
        expired_tc_stamp = self.search(domain_expired_stamp)
        expired_tc_stamp.set_expired_stamp()

        return dict(expiration_stamp=tc_stamp_expired.ids, expired_stamp=expired_tc_stamp.ids)

    @api.model
    def change_expiration_tc_stamp(self):
        today = fields.Date.today()
        next_month = fields.Date.to_string(fields.Date.from_string(today) + relativedelta(months=1))

        # set to expiration tc if date is in less than a month
        domain_stamp = [('date_expiration_authenticated_seal', '>', next_month), '|', ('is_stamp_to_expire', '=', True), ('is_expired_stamp', '=', True)]
        tc_stamp = self.search(domain_stamp)
        tc_stamp.set_stamp_to_expire_false()
        tc_stamp.set_expired_stamp_false()

        return dict(stamp_tc=tc_stamp.ids)
