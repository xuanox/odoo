# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from dateutil.relativedelta import relativedelta
from datetime import date, datetime, timedelta

class equipment_equipment(models.Model):
    _inherit = "equipment.equipment"

    ticket_ids = fields.One2many('helpdesk.ticket', 'equipment_id')
    assign_date = fields.Date('Assigned Date', track_visibility='onchange')
    effective_date = fields.Date('Effective Date', default=fields.Date.context_today, required=True, help="Date at which the equipment became effective. This date will be used to compute the Mean Time Between Failure.")
    cost = fields.Float('Cost')

    period = fields.Integer('Days between each preventive ticket')
    next_action_date = fields.Date(compute='_compute_next_ticket', string='Date of the next preventive ticket', store=True)
    ticket_duration = fields.Float(help="ticket Duration in hours.")

    expected_mtbf = fields.Integer(string='Expected MTBF', help='Expected Mean Time Between Failure')
    mtbf = fields.Integer(compute='_compute_ticket_request', string='MTBF', help='Mean Time Between Failure, computed based on done corrective tickets.')
    mttr = fields.Integer(compute='_compute_ticket_request', string='MTTR', help='Mean Time To Repair')
    estimated_next_failure = fields.Date(compute='_compute_ticket_request', string='Estimated time before next failure (in days)', help='Computed as Latest Failure Date + MTBF')
    latest_failure_date = fields.Date(compute='_compute_ticket_request', string='Latest Failure Date')

    @api.multi
    def _compute_ticket_request(self):
        for equipment in self:
            ticket_requests = equipment.ticket_ids.filtered(lambda x: x.ticket_type_id == '3' and x.stage_id == '3')
            mttr_days = 0
            for ticket in ticket_requests:
                if ticket.stage_id == '3' and ticket.date_close:
                    mttr_days += (ticket.date_close - ticket.request_date).days
            equipment.mttr = len(ticket_requests) and (mttr_days / len(ticket_requests)) or 0
            ticket = ticket_requests.sorted(lambda x: x.request_date)
            if len(ticket) >= 1:
                equipment.mtbf = (ticket[-1].request_date - equipment.effective_date).days / len(ticket)
            equipment.latest_failure_date = ticket and ticket[-1].request_date or False
            if equipment.mtbf:
                equipment.estimated_next_failure = equipment.latest_failure_date + relativedelta(days=equipment.mtbf)
            else:
                equipment.estimated_next_failure = False

    @api.depends('effective_date', 'period', 'ticket_ids.request_date', 'ticket_ids.date_close')
    def _compute_next_ticket(self):
        date_now = fields.Date.context_today(self)
        for equipment in self.filtered(lambda x: x.period > 0):
            next_ticket_todo = self.env['helpdesk.ticket'].search([
                ('equipment_id', '=', equipment.id),
                ('ticket_type_id', '=', '3'),
                ('stage_id', '=', '3'),
                ('date_close', '=', False)], order="request_date asc", limit=1)
            last_ticket_done = self.env['helpdesk.ticket'].search([
                ('equipment_id', '=', equipment.id),
                ('ticket_type_id', '=', '3'),
                ('stage_id', '=', '3'),
                ('date_close', '!=', False)], order="date_close desc", limit=1)
            if next_ticket_todo and last_ticket_done:
                next_date = next_ticket_todo.request_date
                date_gap = next_ticket_todo.request_date - last_ticket_done.date_close
                # If the gap between the last_ticket_done and the next_ticket_todo one is bigger than 2 times the period and next request is in the future
                # We use 2 times the period to avoid creation too closed request from a manually one created
                if date_gap > timedelta(0) and date_gap > timedelta(days=equipment.period) * 2 and next_ticket_todo.request_date > date_now:
                    # If the new date still in the past, we set it for today
                    if last_ticket_done.date_close + timedelta(days=equipment.period) < date_now:
                        next_date = date_now
                    else:
                        next_date = last_ticket_done.date_close + timedelta(days=equipment.period)
            elif next_ticket_todo:
                next_date = next_ticket_todo.request_date
                date_gap = next_ticket_todo.request_date - date_now
                # If next ticket to do is in the future, and in more than 2 times the period, we insert an new request
                # We use 2 times the period to avoid creation too closed request from a manually one created
                if date_gap > timedelta(0) and date_gap > timedelta(days=equipment.period) * 2:
                    next_date = date_now + timedelta(days=equipment.period)
            elif last_ticket_done:
                next_date = last_ticket_done.date_close + timedelta(days=equipment.period)
                # If when we add the period to the last ticket done and we still in past, we plan it for today
                if next_date < date_now:
                    next_date = date_now
            else:
                next_date = self.effective_date + timedelta(days=equipment.period)
            equipment.next_action_date = next_date

    def _create_new_request(self, date):
        self.ensure_one()
        self.env['helpdesk.ticket'].create({
            'description': _('Preventive ticket - %s') % self.name,
            'request_date': date,
            'schedule_date': date,
            'equipment_id': self.id,
            'ticket_type_id': '3',
            'duration': self.ticket_duration,
            })

    @api.model
    def _cron_generate_requests(self):
        """
            Generates ticket request on the next_action_date or today if none exists
        """
        for equipment in self.search([('period', '>', 0)]):
            next_requests = self.env['helpdesk.ticket'].search([('stage_id', '=', '3'),
                                                    ('equipment_id', '=', equipment.id),
                                                    ('ticket_type_id', '=', '3'),
                                                    ('request_date', '=', equipment.next_action_date)])
            if not next_requests:
                equipment._create_new_request(equipment.next_action_date)

class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    schedule_date = fields.Datetime('Scheduled Date', help="Date the ticket team plans the ticket.  It should not differ much from the Request Date. ")
    request_date = fields.Date('Request Date', track_visibility='onchange', default=fields.Date.context_today, help="Date requested for the ticket to happen")
    date_close = fields.Date('Date Close', default=fields.Date.context_today, help="Date the ticket was finished. ")
    duration = fields.Float(help="Duration in hours and minutes.")
