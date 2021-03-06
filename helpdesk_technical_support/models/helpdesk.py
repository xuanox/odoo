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
    _rec_name = 'id'

    def _technical_support_count(self):
        order = self.env['technical_support.order']
        for ticket in self:
            self.technical_support_count = order.search_count([('ticket_id', '=', ticket.id)])

    order_ids=fields.One2many('technical_support.order','ticket_id', string='Orders')
    user_id = fields.Many2one(readonly=True)
    equipment_id=fields.Many2one('equipment.equipment', string='Equipment', required=True)
    client_id = fields.Many2one('res.partner', related='partner_id.commercial_partner_id', string='Cliente', store=True)
    brand_id=fields.Many2one('equipment.brand', related='equipment_id.brand_id', string='Brand', readonly=True)
    zone_id=fields.Many2one('equipment.zone', related='equipment_id.zone_id', string='Zone', readonly=True)
    model_id=fields.Many2one('equipment.model', related='equipment_id.model_id', string='Model', readonly=True)
    parent_id=fields.Many2one('equipment.equipment', related='equipment_id.parent_id', string='Equipment Relation', readonly=True)
    modality_id=fields.Many2one('equipment.modality', related='equipment_id.modality_id', string='Modality', readonly=True, store=True)
    equipment_state_id = fields.Many2one('equipment.state', related='equipment_id.maintenance_state_id', string='Equipment State', readonly=True, store=True, track_visibility='onchange', domain=[('team','=','3')])

    warranty_start_date = fields.Date('Warranty Start', related='equipment_id.warranty_start_date')
    warranty_end_date = fields.Date('Warranty End', related='equipment_id.warranty_end_date')
    dealer_warranty_start_date = fields.Date('Dealer Warranty Start', related='equipment_id.dealer_warranty_start_date')
    dealer_warranty_end_date = fields.Date('Dealer Warranty End', related='equipment_id.dealer_warranty_end_date')

    equipment_number = fields.Char('Equipment Number', related='equipment_id.equipment_number')
    serial = fields.Char('Serial no.', related='equipment_id.serial')
    location = fields.Char('Location', related='equipment_id.location')

    detail_reason = fields.Text('Detail Reason', readonly=True)
    pending_reason = fields.Many2one('helpdesk.ticket.pending.reason', string='Pending Reason', index=True, track_visibility='onchange')

    detail_cause = fields.Text('Detail Causa', readonly=True)
    cause_reason = fields.Many2one('helpdesk.ticket.cause.reason', string='cause Reason', index=True, track_visibility='onchange')
    remote = fields.Boolean('Remote Attention', copy=False)
    observation = fields.Boolean('Observation', copy=False)
    date_planned = fields.Datetime('Planned Date', default=time.strftime('%Y-%m-%d %H:%M:%S'), track_visibility='onchange')
    date_entry = fields.Datetime('Planned Date', default=time.strftime('%Y-%m-%d %H:%M:%S'), track_visibility='onchange')

    technical_support_count = fields.Integer(compute='_technical_support_count', string='# Reports')
    duration = fields.Float('Real Duration', store=True)

    total_days = fields.Integer(string="Days", store=True, compute="_compute_total_time")
    total_time = fields.Float(string="Time (HH:MM)", digits=(16,2), store=True, compute="_compute_total_time")

    @api.depends('date_planned', "close_date")
    def _compute_total_time(self):
        for state in self:
            diff_timedelta = (state.close_date or fields.Datetime.now()) - state.date_planned
            diff_seconds = diff_timedelta.days * 24 * 3600 + diff_timedelta.seconds
            diff_minutes, diff_seconds = divmod(diff_seconds, 60)
            diff_hours, diff_minutes = divmod(diff_minutes, 60)
            diff_days, diff_hours = divmod(diff_hours, 24)
            state.total_days = diff_days
            state.total_time = diff_hours + (diff_minutes/60)

    @api.onchange('equipment_id','team_id')
    def onchange_equipment(self):
        if self.equipment_id:
            self.team_id = self.equipment_id.team_id

    def action_confirm_main(self):
        order = self.env['technical_support.order']
        order_id = False
        for request in self:
            order_id = order.create({
                'date_planned':request.date_planned,
                'date_scheduled':request.date_planned,
                'date_execution':request.date_planned,
                'date_finish':request.date_planned,
                'origin': request.id,
                'user_id': request.user_id.id,
                'state': 'draft',
                'maintenance_type': 'cm',
                'equipment_id': request.equipment_id.id,
                'description': request.name,
                'problem_description': request.description,
                'ticket_type_id': request.ticket_type_id.id,
                'ticket_id': request.id,
            })
        return order_id.id

    def action_confirm_schedule(self):
        order = self.env['technical_support.order']
        order_id = False
        for request in self:
            order_id = order.create({
                'date_planned':request.date_planned,
                'date_scheduled':request.date_planned,
                'date_execution':request.date_planned,
                'date_finish':request.date_planned,
                'origin': request.id,
                'user_id': request.user_id.id,
                'state': 'draft',
                'maintenance_type': 'cm',
                'equipment_id': request.equipment_id.id,
                'description': request.name,
                'problem_description': request.description,
                'ticket_type_id': request.ticket_type_id.id,
                'ticket_id': request.id,
            })
            self.action_schedule()
        return order_id.id

    def action_view_report(self):
        return {
            'domain': "[('ticket_id','in',[" + ','.join(map(str, self.ids)) + "])]",
            'name': _('Technical Support Orders'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'technical_support.order',
            'type': 'ir.actions.act_window',
            'target': 'current',
        }

    def action_pending(self):
        self.write({'stage_id': 10})
        return True

    def action_schedule(self):
        self.write({'stage_id': 14})
        return True

    def action_cause(self):
        self.write({'stage_id': 3})
        return True

    def update_equipment_state_operative(self):
        for order in self:
            if order.equipment_id:
                order.equipment_id.write({'maintenance_state_id': 21})
        return True

    def update_equipment_state_breakdown(self):
        for order in self:
            if order.equipment_id:
                order.equipment_id.write({'maintenance_state_id': 18})
        return True

    @api.multi
    def button_start(self):
        self.ensure_one()
        # Need a loss in case of the real time exceeding the expected
        timeline = self.env['equipment.history.state']

        for workorder in self:
            if workorder.equipment_id.maintenance_state_id != 21:
                workorder.equipment_id.write({
                    'maintenance_state_id': 18,
                    'date_start': datetime.now(),
                })
            timeline.create({
                'ticket_id': workorder.id,
                'name': _('Time Tracking: ')+self.env.user.name,
                'equipment_id': workorder.equipment_id.id,
                'equipment_state_id': 18,
                'date_start': datetime.now(),
                'user_id': self.env.user.id
            })
        return self.equipment_id.write({'maintenance_state_id': 18,
                    'date_start': datetime.now(),
        })

    @api.multi
    def button_finish(self):
        self.ensure_one()
        self.end_all()
        return self.equipment_id.write({'maintenance_state_id': 21, 'date_end': fields.Datetime.now()})

    @api.multi
    def end_previous(self, doall=False):
        """
        @param: doall:  This will close all open time lines on the open work orders when doall = True, otherwise
        only the one of the current user
        """
        # TDE CLEANME
        timeline_obj = self.env['equipment.history.state']
        domain = [('ticket_id', 'in', self.ids), ('date_end', '=', False)]
        for timeline in timeline_obj.search(domain, limit=1):
            wo = timeline.ticket_id
            timeline.write({'date_end': fields.Datetime.now()})
        return True

    @api.multi
    def end_all(self):
        return self.end_previous(doall=True)


class HelpdeskTeam(models.Model):
    _inherit = 'helpdesk.team'

    leader_id=fields.Many2one('res.users', string='Leader')


class HelpdeskTicketPendingReason(models.Model):
    _name = "helpdesk.ticket.pending.reason"
    _description = 'Helpdesk Ticket - Pending Reason'

    name = fields.Char('Name', required=True, translate=True)
    active = fields.Boolean('Active', default=True)

class HelpdeskTicketCauseReason(models.Model):
    _name = "helpdesk.ticket.cause.reason"
    _description = 'Helpdesk Ticket - cause Reason'

    name = fields.Char('Name', required=True, translate=True)
    active = fields.Boolean('Active', default=True)
