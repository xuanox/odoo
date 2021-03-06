# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from dateutil.relativedelta import relativedelta
from datetime import date, datetime, timedelta

class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    subscription_id = fields.One2many('sale.subscription.equipment', related='equipment_id.subscription_ids', string='Subscription')
