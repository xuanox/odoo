# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, SUPERUSER_ID, _, exceptions
import time
import datetime as dt
import time, datetime
from datetime import date
from datetime import datetime
from dateutil import relativedelta
from datetime import datetime, timedelta
from odoo.exceptions import UserError
from dateutil.relativedelta import *


class Part(models.Model):
    _inherit = 'part.order'

    request_id = fields.Many2one('technical_support.request', string='Request', track_visibility='onchange', readonly=True, states={'draft':[('readonly',False)]})

    @api.onchange('request_id')
    def onchange_request(self):
        self.equipment_id = self.request_id.equipment_id
        self.partner_id = self.request_id.client_id

class PartLine(models.Model):
    _inherit = 'part.line'

    request_id = fields.Many2one('technical_support.request', string='Request', track_visibility='onchange')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            move = self.env['part.order'].browse(vals['part_id'])
            vals['request_id'] = move.request_id.id
        lines = super(PartLine, self).create(vals_list)
        return lines
