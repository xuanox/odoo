# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from dateutil.relativedelta import relativedelta
from datetime import date, datetime, timedelta

class AssetAsset(models.Model):
    _inherit = "asset.asset"

    maintenance_ids = fields.One2many('mro.order', 'asset_id')
    assign_date = fields.Date('Assigned Date', track_visibility='onchange')
    effective_date = fields.Date('Effective Date', default=fields.Date.context_today, required=True, help="Date at which the asset became effective. This date will be used to compute the Mean Time Between Failure.")
    cost = fields.Float('Cost')

    period = fields.Integer('Days between each preventive maintenance')
    next_action_date = fields.Date(compute='_compute_next_maintenance', string='Date of the next preventive maintenance', store=True)
    maintenance_duration = fields.Float(help="Maintenance Duration in hours.")

    expected_mtbf = fields.Integer(string='Expected MTBF', help='Expected Mean Time Between Failure')
    mtbf = fields.Integer(compute='_compute_maintenance_request', string='MTBF', help='Mean Time Between Failure, computed based on done corrective maintenances.')
    mttr = fields.Integer(compute='_compute_maintenance_request', string='MTTR', help='Mean Time To Repair')
    estimated_next_failure = fields.Date(compute='_compute_maintenance_request', string='Estimated time before next failure (in days)', help='Computed as Latest Failure Date + MTBF')
    latest_failure_date = fields.Date(compute='_compute_maintenance_request', string='Latest Failure Date')

    @api.multi
    def _compute_maintenance_request(self):
        for equipment in self:
            maintenance_requests = equipment.maintenance_ids.filtered(lambda x: x.maintenance_type == 'cm' and x.state == 'done')
            mttr_days = 0
            for maintenance in maintenance_requests:
                if maintenance.state == 'done' and maintenance.close_date:
                    mttr_days += (maintenance.close_date - maintenance.request_date).days
            equipment.mttr = len(maintenance_requests) and (mttr_days / len(maintenance_requests)) or 0
            maintenance = maintenance_requests.sorted(lambda x: x.request_date)
            if len(maintenance) >= 1:
                equipment.mtbf = (maintenance[-1].request_date - equipment.effective_date).days / len(maintenance)
            equipment.latest_failure_date = maintenance and maintenance[-1].request_date or False
            if equipment.mtbf:
                equipment.estimated_next_failure = equipment.latest_failure_date + relativedelta(days=equipment.mtbf)
            else:
                equipment.estimated_next_failure = False

    @api.depends('effective_date', 'period', 'maintenance_ids.request_date', 'maintenance_ids.close_date')
    def _compute_next_maintenance(self):
        date_now = fields.Date.context_today(self)
        for equipment in self.filtered(lambda x: x.period > 0):
            next_maintenance_todo = self.env['mro.order'].search([
                ('asset_id', '=', equipment.id),
                ('maintenance_type', '=', 'pm'),
                ('state', '=', 'done'),
                ('close_date', '=', False)], order="request_date asc", limit=1)
            last_maintenance_done = self.env['mro.order'].search([
                ('asset_id', '=', equipment.id),
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
                next_date = self.effective_date + timedelta(days=equipment.period)
            equipment.next_action_date = next_date

    def _create_new_request(self, date):
        self.ensure_one()
        self.env['mro.order'].create({
            'description': _('Preventive Maintenance - %s') % self.name,
            'request_date': date,
            'schedule_date': date,
            'asset_id': self.id,
            'maintenance_type': 'pm',
            'duration': self.maintenance_duration,
            })

    @api.model
    def _cron_generate_requests(self):
        """
            Generates maintenance request on the next_action_date or today if none exists
        """
        for equipment in self.search([('period', '>', 0)]):
            next_requests = self.env['mro.order'].search([('state', '=', 'done'),
                                                    ('asset_id', '=', equipment.id),
                                                    ('maintenance_type', '=', 'pm'),
                                                    ('request_date', '=', equipment.next_action_date)])
            if not next_requests:
                equipment._create_new_request(equipment.next_action_date)

class mro_order(models.Model):
    _inherit = "mro.order"

    schedule_date = fields.Datetime('Scheduled Date', help="Date the maintenance team plans the maintenance.  It should not differ much from the Request Date. ")
    request_date = fields.Date('Request Date', track_visibility='onchange', default=fields.Date.context_today, help="Date requested for the maintenance to happen")
    close_date = fields.Date('Close Date', default=fields.Date.context_today, help="Date the maintenance was finished. ")
    duration = fields.Float(help="Duration in hours and minutes.")
