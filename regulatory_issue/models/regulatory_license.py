# -*- coding: utf-8 -*-
###################################################################################
#
#    Electrónica Médica.
#    Copyright (C) 2019-TODAY Electrónica Médica (<https://www.electronicamedica.com>).
#
#    Author: Rocendo Tejada (<https://www.electronicamedica.com>)
#
#
###################################################################################

from datetime import date, datetime, timedelta
from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError


class RegulatoryLicense(models.Model):
    _name = 'regulatory.license'
    _description = 'Regulatory License'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name asc'

    STATE_SELECTION = [
        ('valid', 'Valid'),
        ('to_expire', 'To Expire'),
        ('expired', 'Expired')
    ]

    name = fields.Char(string="License", required=True, translate=True)
    expiration_date = fields.Date(string='Expiration Date')
    description=fields.Text(string='Description')
    file=fields.Binary(string='File')
    email=fields.Char(string='Notification Mail', help="Email address of the Team")
    state = fields.Selection(STATE_SELECTION, 'Status', readonly=True, track_visibility='onchange',
        help="When the maintenance order is created the status is set to 'New'.\n\
        If the License is Valid the status is set to 'Valid'.\n\
        If the License is to Expire then the status is set to 'TC to Expire'.\n\
        If the License is Expired, the status is set to 'Expired TC'.", default='valid')
    is_expired = fields.Boolean('Expired', track_visibility=True)

    def set_to_valid(self):
        return self.write({'state': 'valid'})

    def set_license_to_expire(self):
        return self.write({'state': 'to_expire'})

    def set_expired_license(self):
        return self.write({'state': 'expired'})

    @api.model
    def _cron_change_state_license(self):
        today = fields.Date.today()
        next_month = fields.Date.to_string(fields.Date.from_string(today) + relativedelta(months=1))

        # set to expiration license if date is in less than a month
        domain_expiration = [('expiration_date', '<', next_month),  '|', ('state', '=', 'expired'), ('state', '=', 'valid')]
        license_expired = self.search(domain_expiration)
        license_expired.set_license_to_expire()

        # set to expiration tc if date is passed
        domain_expired = [('expiration_date', '<', today), '|', ('state', '=', 'to_expire'), ('state', '=', 'valid')]
        expired_license = self.search(domain_expired)
        expired_license.set_expired_license()

        return dict(expiration_license=license_expired.ids, expired_license=expired_license.ids)
