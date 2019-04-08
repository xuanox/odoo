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

class Tender(models.Model):
    _inherit = 'crm.lead'

    tender = fields.Boolean('Tender')

class TenderLine(models.Model):
    _description = 'Tender Line'
    _name = 'tender.line'

    name = fields.Char('Line', required=True, translate=True)
