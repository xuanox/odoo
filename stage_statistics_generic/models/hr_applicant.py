# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import date
from odoo import api, fields, models


class Applicant(models.Model):
    _inherit = "hr.applicant"

    applicant_stage_ids = fields.One2many('hr.applicant.history', 'applicant_id', string="Applicant History")

    @api.multi
    def message_track(self, tracked_fields, initial_values):
        for applicant in self:
            if applicant and initial_values and applicant.stage_id != initial_values.get(applicant.id).get('stage_id'):
                if applicant.applicant_stage_ids:
                    applicant.applicant_stage_ids[-1].exit_date = date.today()

                applicant.env['hr.applicant.history'].create({
                    'name': applicant.name,
                    'stage_id': applicant.stage_id.id,
                    'entry_date': date.today(),
                    'applicant_id': applicant.id,
                    'person_assign_id': self.user_id.id,
                })

        return super(Applicant, self).message_track(tracked_fields, initial_values)


class ApplicantHistory(models.Model):
    _name = "hr.applicant.history"
    _description = "Applicant History"

    @api.depends('entry_date', "exit_date")
    def _compute_total_time(self):
        for applicant in self:
            if applicant.exit_date:
                applicant.total_time = (applicant.exit_date - applicant.entry_date).days
            else:
                applicant.total_time = (date.today() - applicant.entry_date).days

    name = fields.Char(string="Task History")
    stage_id = fields.Many2one('hr.recruitment.stage', string='Stage')
    entry_date = fields.Date(string="Stage Entry")
    exit_date = fields.Date(string="Stage Exit")
    total_time = fields.Integer(string="Total Time", store=True, compute="_compute_total_time")
    person_assign_id = fields.Many2one('res.users', string="Person Assigned")
    applicant_id = fields.Many2one('hr.applicant', string="Applicant")
