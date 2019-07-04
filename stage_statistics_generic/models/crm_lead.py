# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import date
from odoo import api, fields, models


class Lead(models.Model):
    _inherit = "crm.lead"

    lead_stage_ids = fields.One2many('lead.history', 'lead_id', string="Lead Stages")

    @api.multi
    def message_track(self, tracked_fields, initial_values):
        for lead in self:

            if lead and initial_values and lead.stage_id != initial_values.get(lead.id).get('stage_id'):
                if lead.lead_stage_ids:
                    lead.lead_stage_ids[-1].exit_date = date.today()

                lead.env['lead.history'].create({
                    'name': lead.name,
                    'stage_id': lead.stage_id.id,
                    'entry_date': date.today(),
                    'lead_id': lead.id,
                    'person_assign_id': self.user_id.id,
                })

        return super(Lead, self).message_track(tracked_fields, initial_values)


class LeadHistory(models.Model):
    _name = "lead.history"
    _description = "Lead History"

    @api.depends('entry_date', "exit_date")
    def _compute_total_time(self):
        for lead in self:
            if lead.exit_date:
                lead.total_time = (lead.exit_date - lead.entry_date).days
            else:
                lead.total_time = (date.today() - lead.entry_date).days

    name = fields.Char(string="Lead/Opportunity")
    stage_id = fields.Many2one('crm.stage', string='Stage')
    entry_date = fields.Date(string="Stage Entry")
    exit_date = fields.Date(string="Stage Exit")
    total_time = fields.Integer(string="Total Time", store=True, compute="_compute_total_time")
    person_assign_id = fields.Many2one('res.users', string="Person Assigned")
    lead_id = fields.Many2one('crm.lead', string="Lead")
