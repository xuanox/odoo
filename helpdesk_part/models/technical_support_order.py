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


class TechnicalSupportOrder(models.Model):
    _inherit = 'technical_support.order'

    part_line_ids = fields.Many2many('part.line', 'technical_support_order_part_line_rel', 'technical_support_order_id', 'part_line_id', string="Orders", copy=False, track_visibility='onchange', states={'done':[('readonly',True)],'cancel':[('readonly',True)]})
