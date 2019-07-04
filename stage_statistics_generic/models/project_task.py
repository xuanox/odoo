# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import date
from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    task_stage_ids = fields.One2many('task.history', 'task_id', string="Task Stages")

    @api.multi
    def message_track(self, tracked_fields, initial_values):
        for task in self:
            if task and initial_values and task.stage_id != initial_values.get(task.id).get('stage_id'):
                if task.task_stage_ids:
                    task.task_stage_ids[-1].exit_date = date.today()

                task.env['task.history'].create({
                    'name': task.name,
                    'stage_id': task.stage_id.id,
                    'entry_date': date.today(),
                    'task_id': task.id,
                    'person_assign_id': self.user_id.id,
                })

        return super(ProjectTask, self).message_track(tracked_fields, initial_values)


class ProjectTaskHistory(models.Model):
    _name = "task.history"
    _description = "Task History"

    @api.depends('entry_date', "exit_date")
    def _compute_total_time(self):
        for task in self:
            if task.exit_date:
                task.total_time = (task.exit_date - task.entry_date).days
            else:
                task.total_time = (date.today() - task.entry_date).days

    name = fields.Char(string="Task History")
    stage_id = fields.Many2one('project.task.type', string='Stage')
    entry_date = fields.Date(string="Stage Entry")
    exit_date = fields.Date(string="Stage Exit")
    total_time = fields.Integer(string="Total Time", store=True, compute="_compute_total_time")
    person_assign_id = fields.Many2one('res.users', string="Person Assigned")
    task_id = fields.Many2one('project.task', string="Task")
