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

class RegulatoryTechnicalFileModification(models.Model):
    _name = 'regulatory.technical.file.modification'
    _description = 'Regulatory Technical File Modification'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    STATE_SELECTION = [
        ('draft', 'New'),
        ('assigned', 'Assigned'),
        ('process', 'In Process'),
        ('scheduled', 'Scheduled'),
        ('done', 'Completed'),
        ('rejected', 'Rejected')
    ]

    def _tfr_count(self):
        request = self.env['regulatory.technical.file.registry']
        for tfr in self:
            self.tfr_count = request.search_count([('tfm_id', '=', tfr.id)])

    @api.multi
    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'state' in init_values and self.state == 'draft':
            return 'regulatory_issue.modification_request_created'
        elif 'state' in init_values and self.state != 'draft':
            return 'regulatory_issue.modification_request_status'
        return super(RegulatoryTechnicalFileModification, self)._track_subtype(init_values)

    name = fields.Char('#Request:', readonly=True, copy=False, required=True, default='New')
    technical_file_id = fields.Many2one('regulatory.technical.file', string='#Technical File', track_visibility='onchange', required=True)
    technical_file_name = fields.Char(related='technical_file_id.technical_file_name', string='Technical File Name', track_visibility='onchange')
    observation=fields.Text('Description', track_visibility='onchange')
    sales_team_id = fields.Many2one('crm.team', string='Sales Team', track_visibility='onchange', default=lambda self: self.env['crm.team'].sudo()._get_default_team_id(user_id=self.env.uid), required=True)
    user_id = fields.Many2one('res.users', string='Responsible AR', track_visibility='onchange', domain=lambda self: [('groups_id', 'in', self.env.ref('regulatory_issue.group_regulatory_issue_manager').id)])
    responsible_id = fields.Many2one('res.users', string='Responsible', track_visibility='onchange', default=lambda self: self.env.user, domain=lambda self: [('groups_id', 'in', self.env.ref('regulatory_issue.group_regulatory_issue_user').id)])
    responsible_sales_id = fields.Many2one('res.users', string='Responsible Sale', track_visibility='onchange', default=lambda self: self.env.user, required=True, domain=lambda self: [('groups_id', 'in', self.env.ref('regulatory_issue.group_regulatory_issue_user').id)])
    responsible_team_lider_id = fields.Many2one('res.users', related='sales_team_id.user_id', string='Team Lider', track_visibility='onchange')
    models_id = fields.Many2one('equipment.model', string='Models Equipments', track_visibility='onchange', required=True)
    brand_id=fields.Many2one('equipment.brand', related='models_id.brand_id', store=True, string='Brand', track_visibility='onchange')
    modification_lines = fields.One2many('regulatory.technical.file.modification.line', 'regulatory_technical_file_modification_id', 'Modification Line', track_visibility='onchange')
    priority = fields.Selection(TICKET_PRIORITY, string='Priority', default='0')
    state = fields.Selection(STATE_SELECTION, 'Status', readonly=True, track_visibility='onchange',
        help="When the maintenance order is created the status is set to 'New'.\n\
        If the order is Assigned the status is set to 'Assigned'.\n\
        If the order is Process the status is set to 'Process'.\n\
        If the order is Homologation the status is set to 'Homologation'.\n\
        If the stock is Completed then the status is set to 'Completed'.\n\
        When the request is over, the status is set to 'Rejected'.", default='draft')
    date_planned = fields.Datetime('Planned Date', track_visibility='onchange')
    entity_id = fields.Many2one('regulatory.entity', string='Entity', track_visibility='onchange')
    location_homologation=fields.Text(related='entity_id.description', string='Homologation Location', readonly=True, track_visibility='onchange')
    tfr_ids = fields.One2many('regulatory.technical.file.registry', 'tfm_id', string='TFR')
    tfr_id = fields.Many2one('regulatory.technical.file.registry', string='TFR', track_visibility='onchange', readonly=True)
    tfr_count = fields.Integer(compute='_tfr_count', string='TFR')
    contact_id = fields.Many2one('res.partner', string='Contact', states={'done': [('readonly', True)]})
    contact_ids = fields.Many2many('res.partner', string='Contacts', states={'done': [('readonly', True)]})
    tag_ids = fields.Many2many('regulatory.tag', 'regulatory_tfm_tag_rel', 'tfm_id', 'tag_id', string='Tags', help="Classify and analyze your request like: Training, Service")

    def action_assigned(self):
        self.write({'state': 'assigned'})
        self.activity_update()
        return True

    def action_process(self):
        self.write({'state': 'process'})
        return True

    def action_scheduled(self):
        self.write({'state': 'scheduled'})
        self.activity_update_scheduled()
        self.activity_update_scheduled_responsible_sales()
        return True

    def action_done(self):
        self.write({'state': 'done'})
        return True

    def action_confirm(self):
        tfr = self.env['regulatory.technical.file.registry']
        tfr_id = False
        for request in self:
            tfr_id = tfr.create({
                'technical_file_id':request.technical_file_id.id,
                'models_id':request.models_id.id,
                'responsible_sales_id':request.responsible_sales_id.id,
                'team_id': request.sales_team_id.id,
                'category': 'update',
                'contact_id':request.contact_id.id,
                'tfm_id': request.id,
            })
        return tfr_id.id


    def action_rejected(self):
        self.write({'state': 'rejected'})
        return True

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('regulatory.technical.file.modification') or '/'
        request = super(RegulatoryTechnicalFileModification, self).create(vals)
        request.activity_update_responsible_team_lider()
        return request

    @api.multi
    def write(self, vals):
        res = super(RegulatoryTechnicalFileModification, self).write(vals)
        if 'state' in vals:
            self.filtered(lambda m: m.state == 'process')
            self.activity_feedback(['regulatory_issue.mail_act_review_regulatory_technical_file_modification'])
        if vals.get('user_id') or vals.get('create_date'):
            self.activity_update()
        if vals.get('models_id'):
            # need to change description of activity also so unlink old and create new activity
            self.activity_unlink(['regulatory_issue.mail_act_review_regulatory_technical_file_modification'])
            self.activity_update()
        return res

    def activity_update_responsible_team_lider(self):
        """ Update maintenance activities based on current record set state.
        It reschedule, unlink or create maintenance request activities. """
        self.filtered(lambda request: not request.create_date).activity_unlink(['regulatory_issue.mail_act_regulatory_technical_file_modification'])
        for request in self.filtered(lambda request: request.create_date):
            date_dl = fields.Datetime.from_string(request.create_date).date()
            updated = request.activity_reschedule(
                ['regulatory_issue.mail_act_regulatory_technical_file_modification'],
                date_deadline=date_dl,
                new_user_id=request.responsible_team_lider_id.id or self.env.uid)
            if not updated:
                if request.models_id:
                    note = _('Assign Priority TFM - This activity is to assign priority to the modification request')
                else:
                    note = False
                request.activity_schedule(
                    'regulatory_issue.mail_act_regulatory_technical_file_modification',
                    fields.Datetime.from_string(request.create_date).date(),
                    note=note, user_id=request.responsible_team_lider_id.id or self.env.uid)

    def activity_update(self):
        """ Update maintenance activities based on current record set state.
        It reschedule, unlink or create maintenance request activities. """
        self.filtered(lambda request: not request.create_date).activity_unlink(['regulatory_issue.mail_act_review_regulatory_technical_file_modification'])
        for request in self.filtered(lambda request: request.create_date):
            date_dl = fields.Datetime.from_string(request.create_date).date()
            updated = request.activity_reschedule(
                ['regulatory_issue.mail_act_review_regulatory_technical_file_modification'],
                date_deadline=date_dl,
                new_user_id=request.user_id.id or self.env.uid)
            if not updated:
                if request.models_id:
                    note = _('Regulatory TFM Review - Review of the Request for Modification of the Technical Data Sheet ')
                else:
                    note = False
                request.activity_schedule(
                    'regulatory_issue.mail_act_review_regulatory_technical_file_modification',
                    fields.Datetime.from_string(request.create_date).date(),
                    note=note, user_id=request.user_id.id or self.env.uid)

    def activity_update_scheduled(self):
        """ Update maintenance activities based on current record set state.
        It reschedule, unlink or create maintenance request activities. """
        self.filtered(lambda request: not request.date_planned).activity_unlink(['regulatory_issue.mail_act_scheduled_ar_regulatory_technical_file_modification'])
        for request in self.filtered(lambda request: request.date_planned):
            date_dl = fields.Datetime.from_string(request.date_planned).date()
            updated = request.activity_reschedule(
                ['regulatory_issue.mail_act_scheduled_ar_regulatory_technical_file_modification'],
                date_deadline=date_dl,
                new_user_id=request.user_id.id or self.env.uid)
            if not updated:
                if request.models_id:
                    note = _('Regulatory Scheduled Appointment')
                else:
                    note = False
                request.activity_schedule(
                    'regulatory_issue.mail_act_scheduled_ar_regulatory_technical_file_modification',
                    fields.Datetime.from_string(request.date_planned).date(),
                    note=note, user_id=request.user_id.id or self.env.uid)

    def activity_update_scheduled_responsible_sales(self):
        """ Update maintenance activities based on current record set state.
        It reschedule, unlink or create maintenance request activities. """
        self.filtered(lambda request: not request.date_planned).activity_unlink(['regulatory_issue.mail_act_scheduled_regulatory_technical_file_modification'])
        for request in self.filtered(lambda request: request.date_planned):
            date_dl = fields.Datetime.from_string(request.date_planned).date()
            updated = request.activity_reschedule(
                ['regulatory_issue.mail_act_scheduled_regulatory_technical_file_modification'],
                date_deadline=date_dl,
                new_user_id=request.responsible_sales_id.id or self.env.uid)
            if not updated:
                if request.models_id:
                    note = _('Regulatory Scheduled Appointment')
                else:
                    note = False
                request.activity_schedule(
                    'regulatory_issue.mail_act_scheduled_regulatory_technical_file_modification',
                    fields.Datetime.from_string(request.date_planned).date(),
                    note=note, user_id=request.responsible_sales_id.id or self.env.uid)

    def action_view_tfr_request(self):
        return {
            'domain': "[('tfm_id','in',[" + ','.join(map(str, self.ids)) + "])]",
            'name': _('Registry Request'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'regulatory.technical.file.registry',
            'type': 'ir.actions.act_window',
            'target': 'current',
        }

class RegulatoryTechnicalFileModificationLine(models.Model):
    _name = 'regulatory.technical.file.modification.line'
    _description = 'Regulatory Technical File Modification Line'

    name = fields.Char('Point to Change', required=True)
    value = fields.Char('Value', required=True)
    regulatory_technical_file_modification_id = fields.Many2one('regulatory.technical.file.modification', 'Regulatory Technical File Modification')
