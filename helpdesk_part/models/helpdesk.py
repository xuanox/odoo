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


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    def _part_count(self):
        request = self.env['part.order']
        for ticket in self:
            self.part_count = request.search_count([('ticket_id', '=', ticket.id)])

    def _part_line_count(self):
        request = self.env['part.line']
        for ticket in self:
            self.part_line_count = request.search_count([('ticket_id', '=', ticket.id)])

    part_ids=fields.One2many('part.order','ticket_id', string='SPR')
    part_count = fields.Integer(compute='_part_count', string='# SPR')
    part_line_count = fields.Integer(compute='_part_line_count', string='# Parts List')

    def action_view_part_request(self):
        return {
            'domain': "[('ticket_id','in',[" + ','.join(map(str, self.ids)) + "])]",
            'name': _('Part Request'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'part.order',
            'type': 'ir.actions.act_window',
            'target': 'current',
        }

    def action_view_part_line_request(self):
        return {
            'domain': "[('ticket_id','in',[" + ','.join(map(str, self.ids)) + "])]",
            'name': _('Part Line Request'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'part.line',
            'type': 'ir.actions.act_window',
            'target': 'current',
        }
