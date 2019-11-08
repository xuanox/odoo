# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo
#    Copyright (C) 2014-2018 emsa (<http://www.electronicamedica.com>).
#
##############################################################################

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from dateutil.relativedelta import relativedelta
from datetime import date, datetime, timedelta

class EquipmentEquipment(models.Model):
    _name = 'equipment.equipment'
    _inherit = 'equipment.equipment'

    def _technical_support_count(self):
        maintenance = self.env['technical_support.order']
        for equipment in self:
            self.technical_support_count = maintenance.search_count([('equipment_id', '=', equipment.id)])

    def _tsr_count(self):
        maintenance = self.env['technical_support.request']
        for equipment in self:
            self.tsr_count = maintenance.search_count([('equipment_id', '=', equipment.id)])

    def _next_maintenance(self):
        maintenance = self.env['technical_support.order']
        for equipment in self:
            order_ids = maintenance.search(
                [('equipment_id', '=', equipment.id),
                ('state', 'not in', ('done','cancel'))],
                limit=1, order='date_execution')
            if len(order_ids) > 0:
                self.maintenance_date = order_ids[0].date_execution

    technical_support_count = fields.Integer(compute='_technical_support_count', string='# TSO')
    tsr_count = fields.Integer(compute='_tsr_count', string='# TSR')
    maintenance_date = fields.Datetime(compute='_next_maintenance', string='Maintenance Date')

    maintenance_ids = fields.One2many('technical_support.request', 'equipment_id', string='TSR')
    period = fields.Integer('Days between each preventive maintenance')
    next_action_date = fields.Date(compute='_compute_next_maintenance', string='Date of the next preventive maintenance', store=True)
    maintenance_duration = fields.Float(help="Maintenance Duration in hours.")

    @api.depends('effective_start_date', 'period', 'maintenance_ids.request_date', 'maintenance_ids.close_date')
    def _compute_next_maintenance(self):
        date_now = fields.Date.context_today(self)
        for equipment in self.filtered(lambda x: x.period > 0):
            next_maintenance_todo = self.env['technical_support.request'].search([
                ('equipment_id', '=', equipment.id),
                ('maintenance_type', '=', 'pm'),
                ('state', '!=', 'done'),
                ('close_date', '=', False)], order="request_date asc", limit=1)
            last_maintenance_done = self.env['technical_support.request'].search([
                ('equipment_id', '=', equipment.id),
                ('maintenance_type', '=', 'pm'),
                ('state', '=', 'done'),
                ('close_date', '!=', False)], order="close_date desc", limit=1)
            if next_maintenance_todo and last_maintenance_done:
                next_date = next_maintenance_todo.request_date
                date_gap = next_maintenance_todo.request_date - last_maintenance_done.close_date
                # If the gap between the last_maintenance_done and the next_maintenance_todo one is bigger than 2 times the period and next request is in the future
                # We use 2 times the period to avoid creation too closed request from a manually one created
                if date_gap > timedelta(0) and date_gap > timedelta(days=equipment.period) * 2 and next_maintenance_todo.request_date > date_now:
                    # If the new date still in the past, we set it for today
                    if last_maintenance_done.close_date + timedelta(days=equipment.period) < date_now:
                        next_date = date_now
                    else:
                        next_date = last_maintenance_done.close_date + timedelta(days=equipment.period)
            elif next_maintenance_todo:
                next_date = next_maintenance_todo.request_date
                date_gap = next_maintenance_todo.request_date - date_now
                # If next maintenance to do is in the future, and in more than 2 times the period, we insert an new request
                # We use 2 times the period to avoid creation too closed request from a manually one created
                if date_gap > timedelta(0) and date_gap > timedelta(days=equipment.period) * 2:
                    next_date = date_now + timedelta(days=equipment.period)
            elif last_maintenance_done:
                next_date = last_maintenance_done.close_date + timedelta(days=equipment.period)
                # If when we add the period to the last maintenance done and we still in past, we plan it for today
                if next_date < date_now:
                    next_date = date_now
            else:
                next_date = self.effective_start_date + timedelta(days=equipment.period)
            equipment.next_action_date = next_date

    def _create_new_request(self, date):
        self.ensure_one()
        self.env['technical_support.request'].create({
            'subject': _('Mantenimiento Preventivo - %s') % self.name,
            'request_date': date,
            'requested_date': date,
            'execution_date': date,
            'schedule_date': date,
            'close_date': date,
            'equipment_id': self.id,
            'client_id': self.client_id.id,
            'maintenance_type': 'pm',
            'duration': self.maintenance_duration,
            })

    @api.model
    def _cron_generate_requests(self):
        """
            Generates maintenance request on the next_action_date or today if none exists
        """
        for equipment in self.search([('period', '>', 0)]):
            next_requests = self.env['technical_support.request'].search([('state', '=', 'draft'),
                                                    ('equipment_id', '=', equipment.id),
                                                    ('maintenance_type', '=', 'pm'),
                                                    ('request_date', '=', equipment.next_action_date)])
            if not next_requests:
                equipment._create_new_request(equipment.next_action_date)


    def action_view_tso(self):
        return {
            'domain': "[('equipment_id','in',[" + ','.join(map(str, self.ids)) + "])]",
            'name': _('TSO'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'technical_support.order',
            'type': 'ir.actions.act_window',
            'target': 'current',
        }

    def action_view_tsr(self):
        return {
            'domain': "[('equipment_id','in',[" + ','.join(map(str, self.ids)) + "])]",
            'name': _('TSR'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'technical_support.request',
            'type': 'ir.actions.act_window',
            'target': 'current',
        }
