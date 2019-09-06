# -*- coding: utf-8 -*-
###################################################################################
#
#    Electrónica Médica.
#    Copyright (C) 2019-TODAY Electrónica Médica (<https://www.electronicamedica.com>).
#
#    Author: Rocendo Tejada (<https://www.electronicamedica.com>)
#
#
###################################################################################
import time
from odoo import api, fields, models, _
from odoo import netsvc
import odoo.addons.decimal_precision as dp
from datetime import date, datetime, timedelta
from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError

TICKET_PRIORITY = [
    ('0', 'All'),
    ('1', 'Low priority'),
    ('2', 'High priority'),
    ('3', 'Urgent'),
]

class RegulatoryTechnicalFileCreationStage(models.Model):
    _name = 'regulatory.technical.file.creation.stage'
    _description = 'Regulatory Technical File Creation Stage'
    _order = 'sequence, id'

    name = fields.Char('Name', required=True, translate=True)
    sequence = fields.Integer('Sequence', default=20)
    fold = fields.Boolean('Folded in Regulatory Technical File Creation Pipe')
    done = fields.Boolean('Request Done')


class RegulatoryTechnicalFileCreation(models.Model):
    _name = 'regulatory.technical.file.creation'
    _description = 'Regulatory Technical File Creation'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    STATE_SELECTION = [
        ('draft', 'New'),
        ('assigned', 'Assigned'),
        ('process', 'In Process'),
        ('homologation', 'In Homologation'),
        ('done', 'Completed'),
        ('rejected', 'Rejected')
    ]

    ENTITY_SELECTION = [
        ('minsa', 'MINSA'),
        ('css', 'CSS'),
    ]

    @api.returns('self')
    def _default_stage(self):
        return self.env['regulatory.technical.file.creation.stage'].search([], limit=1)

    name = fields.Char('#Request:', readonly=True, copy=False, required=True, default='New')
    technical_file_name = fields.Char(string="Proposed Name for the File", required=True, track_visibility='onchange')
    observation=fields.Text('Observation', track_visibility='onchange')
    responsible_id = fields.Many2one('res.users', string='Responsible AR', track_visibility='onchange', default=lambda self: self.env.user)
    user_id = fields.Many2one('res.users', string='Responsible AR', track_visibility='onchange')
    responsible_sales_id = fields.Many2one('res.users', string='Responsible Sale', track_visibility='onchange', default=lambda self: self.env.user, required=True)
    sales_team_id = fields.Many2one('crm.team', string='Sales Team', track_visibility='onchange')
    responsible_team_lider_id = fields.Many2one('res.users', related='sales_team_id.user_id', string='Team Lider', track_visibility='onchange')
    models_id = fields.Many2one('equipment.model', string='Model Equipment', track_visibility='onchange', required=True)
    brand_id=fields.Many2one('equipment.brand', related='models_id.brand_id', track_visibility='onchange', store=True, string='Brand')
    stage_id = fields.Many2one('regulatory.technical.file.creation.stage', string='Stage', track_visibility='onchange', default=_default_stage)
    priority = fields.Selection(TICKET_PRIORITY, string='Priority', default='0')
    state = fields.Selection(STATE_SELECTION, 'Status', readonly=True, track_visibility='onchange',
        help="When the maintenance order is created the status is set to 'New'.\n\
        If the order is Assigned the status is set to 'Assigned'.\n\
        If the order is Process the status is set to 'Process'.\n\
        If the order is Homologation the status is set to 'Homologation'.\n\
        If the stock is Completed then the status is set to 'Completed'.\n\
        When the request is over, the status is set to 'Rejected'.", default='draft')
    technical_file_id = fields.Many2one('regulatory.technical.file', string='Technical File Number', required=True, track_visibility='onchange')
    technical_file_name = fields.Char(related='technical_file_id.technical_file_name', string='Technical File Name', track_visibility='onchange')
    entity_reference = fields.Char('Entity Reference', copy=False)
    date_planned = fields.Datetime('Planned Date', default=time.strftime('%Y-%m-%d %H:%M:%S'), track_visibility='onchange')
    entity_id = fields.Many2one('regulatory.entity', string='Entity', track_visibility='onchange')
    location_homologation=fields.Text(related='entity_id.description', string='Homologation Location', readonly=True)

    def action_assigned(self):
        self.write({'state': 'assigned'})
        return True

    def action_process(self):
        self.write({'state': 'process'})
        return True

    def action_homologation(self):
        self.activity_update()
        self.write({'state': 'homologation'})
        return True

    def action_done(self):
        self.write({'state': 'done'})
        return True

    def action_rejected(self):
        self.write({'state': 'rejected'})
        return True

    @api.model
    def create(self, vals):
        if vals.get('name','/')=='/':
            vals['name'] = self.env['ir.sequence'].next_by_code('regulatory.technical.file.creation') or '/'
        request = super(RegulatoryTechnicalFileCreation, self).create(vals)
        request.activity_update_responsible_team_lider()
        return request

    @api.multi
    def write(self, vals):
        res = super(RegulatoryTechnicalFileCreation, self).write(vals)
        if 'state' in vals:
            self.filtered(lambda m: m.state == 'process')
            self.activity_feedback(['regulatory_issue.mail_act_regulatory_technical_file_creation'])
        if vals.get('user_id') or vals.get('create_date'):
            self.activity_update()
        if vals.get('models_id'):
            # need to change description of activity also so unlink old and create new activity
            self.activity_unlink(['regulatory_issue.mail_act_regulatory_technical_file_creation'])
            self.activity_update_responsible_team_lider()
        return res

    def activity_update_responsible_team_lider(self):
        """ Update maintenance activities based on current record set state.
        It reschedule, unlink or create maintenance request activities. """
        self.filtered(lambda request: not request.create_date).activity_unlink(['regulatory_issue.mail_act_regulatory_technical_file_creation'])
        for request in self.filtered(lambda request: request.create_date):
            date_dl = fields.Datetime.from_string(request.create_date).date()
            updated = request.activity_reschedule(
                ['regulatory_issue.mail_act_regulatory_technical_file_creation'],
                date_deadline=date_dl,
                new_user_id=request.responsible_team_lider_id.id or self.env.uid)
            if not updated:
                if request.models_id:
                    note = _('Priority Request Creation for <a href="#" data-oe-model="%s" data-oe-id="%s">%s</a>')
                else:
                    note = False
                request.activity_schedule(
                    'regulatory_issue.mail_act_regulatory_technical_file_creation',
                    fields.Datetime.from_string(request.create_date).date(),
                    note=note, user_id=request.responsible_team_lider_id.id or self.env.uid)


    def activity_update(self):
        """ Update maintenance activities based on current record set state.
        It reschedule, unlink or create maintenance request activities. """
        self.filtered(lambda request: not request.create_date).activity_unlink(['regulatory_issue.mail_act_regulatory_technical_file_creation'])
        for request in self.filtered(lambda request: request.create_date):
            date_dl = fields.Datetime.from_string(request.create_date).date()
            updated = request.activity_reschedule(
                ['regulatory_issue.mail_act_regulatory_technical_file_creation'],
                date_deadline=date_dl,
                new_user_id=request.user_id.id or self.env.uid)
            if not updated:
                if request.models_id:
                    note = _('Priority Request Creation for <a href="#" data-oe-model="%s" data-oe-id="%s">%s</a>')
                else:
                    note = False
                request.activity_schedule(
                    'regulatory_issue.mail_act_regulatory_technical_file_creation',
                    fields.Datetime.from_string(request.create_date).date(),
                    note=note, user_id=request.user_id.id or self.env.uid)
