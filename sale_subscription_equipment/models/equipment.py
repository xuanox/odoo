# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from dateutil.relativedelta import relativedelta
from datetime import date, datetime, timedelta

class equipment_equipment(models.Model):
    _inherit = "equipment.equipment"

    def _subscription_count(self):
        subscription = self.env['sale.subscription.equipment']
        for equipment in self:
            self.subscription_count = subscription.search_count([('equipment_id', '=', equipment.id)])

    subscription_ids = fields.One2many('sale.subscription.equipment', 'equipment_id')
    subscription_count = fields.Integer(compute='_subscription_count', string='# Subscriptions')
