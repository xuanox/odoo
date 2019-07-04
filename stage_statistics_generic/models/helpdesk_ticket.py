# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import date
from odoo import api, fields, models


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    ticket_stage_ids = fields.One2many('helpdesk.ticket.history', 'ticket_id', string="Task Stages")

    @api.multi
    def message_track(self, tracked_fields, initial_values):
        for ticket in self:
            if ticket and initial_values and ticket.stage_id != initial_values.get(ticket.id).get('stage_id'):
                if ticket.ticket_stage_ids:
                    ticket.ticket_stage_ids[-1].exit_date = date.today()

                ticket.env['helpdesk.ticket.history'].create({
                    'name': ticket.name,
                    'stage_id': ticket.stage_id.id,
                    'entry_date': date.today(),
                    'ticket_id': ticket.id,
                    'person_assign_id': self.user_id.id,
                })

        return super(HelpdeskTicket, self).message_track(tracked_fields, initial_values)


class HelpdeskTicketHistory(models.Model):
    _name = "helpdesk.ticket.history"
    _description = "Helpdesk Ticket History"

    @api.depends('entry_date', "exit_date")
    def _compute_total_time(self):
        for ticket in self:
            if ticket.exit_date:
                ticket.total_time = (ticket.exit_date - ticket.entry_date).days
            else:
                ticket.total_time = (date.today() - ticket.entry_date).days

    name = fields.Char(string="Task History")
    stage_id = fields.Many2one('helpdesk.stage', string='Stage')
    entry_date = fields.Date(string="Stage Entry")
    exit_date = fields.Date(string="Stage Exit")
    total_time = fields.Integer(string="Total Time", store=True, compute="_compute_total_time")
    person_assign_id = fields.Many2one('res.users', string="Person Assigned")
    ticket_id = fields.Many2one('helpdesk.ticket', string="Ticket")
