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


class TechnicalSupportRequest(models.Model):
    _inherit = 'technical_support.request'

    def _part_count(self):
        request = self.env['part.order']
        for ticket in self:
            self.part_count = request.search_count([('request_id', '=', ticket.id)])

    def _part_line_count(self):
        request = self.env['part.line']
        for ticket in self:
            self.part_line_count = request.search_count([('request_id', '=', ticket.id)])

    part_ids=fields.One2many('part.order','request_id', string='Parts Request')
    part_count = fields.Integer(compute='_part_count', string='# Parts Request')
    part_line_count = fields.Integer(compute='_part_line_count', string='# Parts List')

    def action_view_part_request(self):
        return {
            'domain': "[('request_id','in',[" + ','.join(map(str, self.ids)) + "])]",
            'name': _('Part Request'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'part.order',
            'type': 'ir.actions.act_window',
            'target': 'current',
        }

    def action_view_part_line_request(self):
        return {
            'domain': "[('request_id','in',[" + ','.join(map(str, self.ids)) + "])]",
            'name': _('Part Line Request'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'part.line',
            'type': 'ir.actions.act_window',
            'target': 'current',
        }

    @api.multi
    def action_submit_expenses(self):
        return {
            'name': _('New SPR Request'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'part.order',
            'target': 'current',
            'context': {
                'default_request_id': self.ids,
                'default_equipment_id': self.equipment_id
            }
        }
