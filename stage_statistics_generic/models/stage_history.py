# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import date
from odoo import api, fields, models

class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    tracking_fields = []

    stage_ids = fields.One2many('stage.history', 'res_id', string="Stage History", domain=lambda self: [('res_model', '=', self._name)], auto_join=True)

    @api.multi
    def message_track(self, tracked_fields, initial_values):
        if self.tracking_fields:
            stage = self.tracking_fields[0]
            for rec in self:
                if 'stage_id' in self.tracking_fields:
                    state_name = rec.stage_id.name
                elif 'state' in self.tracking_fields:
                    state_name = rec.state
                elif 'quality_state' in self.tracking_fields:
                    state_name = rec.quality_state
                else:
                    state_name = False

                flag = False
                if self._fields[stage].type == 'selection':
                    if rec and initial_values and initial_values.get(rec.id).get(self.tracking_fields[0]) and state_name != initial_values.get(rec.id).get(self.tracking_fields[0]):
                        flag = True
                if self._fields[stage].type == 'many2one':
                    if rec and initial_values and initial_values.get(rec.id).get(self.tracking_fields[0]) and state_name != initial_values.get(rec.id).get(self.tracking_fields[0]).name:
                        flag = True

                if flag:
                    if rec.stage_ids:
                        rec.stage_ids[-1].exit_date = fields.Datetime.now()

                    if 'team_id' in self.tracking_fields:
                        person_assign = rec.team_id.id
                    elif len(self.tracking_fields) > 1:
                        person_assign = rec.user_id.id
                    else:
                        person_assign = False

                    rec.env['stage.history'].create({
                        'name': rec.name,
                        'stage': state_name,
                        'entry_date': fields.Datetime.now(),
                        'res_id': rec.id,
                        'res_model': rec._name,
                        'person_assign_id': person_assign,
                    })

        return super(MailThread, self).message_track(tracked_fields, initial_values)


class StageHistory(models.Model):
    _name = "stage.history"
    _description = "Stage History"

    @api.depends('entry_date', "exit_date")
    def _compute_total_time(self):
        for state in self:
            diff_timedelta = (state.exit_date or fields.Datetime.now()) - state.entry_date
            diff_seconds = diff_timedelta.days * 24 * 3600 + diff_timedelta.seconds
            diff_minutes, diff_seconds = divmod(diff_seconds, 60)
            diff_hours, diff_minutes = divmod(diff_minutes, 60)
            diff_days, diff_hours = divmod(diff_hours, 24)
            state.total_days = diff_days
            state.total_time = diff_hours + (diff_minutes/60)

    name = fields.Char()
    stage = fields.Char(string='Stage')
    entry_date = fields.Datetime(string="Stage Entry")
    exit_date = fields.Datetime(string="Stage Exit")
    total_days = fields.Integer(string="Days", store=True, compute="_compute_total_time")
    total_time = fields.Float(string="Time (HH:MM)", digits=(16,2), store=True, compute="_compute_total_time")
    person_assign_id = fields.Many2one('res.users', string="Person Assigned")
    res_id = fields.Integer(string='Message ID')
    res_model = fields.Char(string='Model')


class Lead(models.Model):
    _inherit = "crm.lead"
    tracking_fields = ['stage_id', 'user_id']


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"
    tracking_fields = ['stage_id', 'user_id']


class Applicant(models.Model):
    _inherit = "hr.applicant"
    tracking_fields = ['stage_id', 'user_id']


class ProjectTask(models.Model):
    _inherit = "project.task"
    tracking_fields = ['stage_id', 'user_id']


class SaleOrder(models.Model):
    _inherit = "sale.order"
    tracking_fields = ['state', 'user_id']


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"
    tracking_fields = ['state', 'user_id']


class Picking(models.Model):
    _inherit = "stock.picking"
    tracking_fields = ['state']


class QualityCheck(models.Model):
    _inherit = "quality.check"
    tracking_fields = ['quality_state', 'team_id']
