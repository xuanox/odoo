# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import date
from odoo import api, fields, models


class QualityCheck(models.Model):
    _inherit = "quality.check"

    quality_stage_ids = fields.One2many('quality.check.history', 'quality_id', string="Lead Stages")

    @api.multi
    def message_track(self, tracked_fields, initial_values):
        for quality in self:
            if quality and initial_values and quality.quality_state != initial_values.get(quality.id).get('quality_state'):
                if quality.quality_stage_ids:
                    quality.quality_stage_ids[-1].exit_date = date.today()

                quality.env['quality.check.history'].create({
                    'name': quality.name,
                    'quality_state': quality.quality_state,
                    'entry_date': date.today(),
                    'quality_id': quality.id,
                    'team_assign_id': self.team_id.id,
                })

        return super(QualityCheck, self).message_track(tracked_fields, initial_values)


class QualityCheckStage(models.Model):
    _name = "quality.check.history"
    _description = "Quality History"

    @api.depends('entry_date', "exit_date")
    def _compute_total_time(self):
        for quality in self:
            if quality.exit_date:
                quality.total_time = (quality.exit_date - quality.entry_date).days
            else:
                quality.total_time = (date.today() - quality.entry_date).days

    name = fields.Char(string="Quality Alert")
    quality_state = fields.Selection([
        ('none', 'To do'),
        ('pass', 'Passed'),
        ('fail', 'Failed')], string='Status')
    entry_date = fields.Date(string="Stage Entry")
    exit_date = fields.Date(string="Stage Exit")
    total_time = fields.Integer(string="Total Time", store=True, compute="_compute_total_time")
    team_assign_id = fields.Many2one('quality.alert.team', string="Team Assigned")
    quality_id = fields.Many2one('quality.check', string="Quality")
