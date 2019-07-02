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

class RegulatoryTechnicalFileTypeArea(models.Model):
    _name = 'regulatory.technical.file.type.area'
    _description = 'Regulatory Technical File Type Area'

    name = fields.Char(string="Technical File Type Area", required=True, translate=True)
    description=fields.Text('Description')


class RegulatoryTechnicalFileGroup(models.Model):
    _name = 'regulatory.technical.file.group'
    _description = 'Regulatory Technical File Group'

    name = fields.Char(string="Technical File Group", required=True, translate=True)
    description=fields.Text('Description')


class RegulatoryTechnicalFileRegistryStage(models.Model):
    _name = 'regulatory.technical.file.registry.stage'
    _description = 'Regulatory Technical File Registry Stage'
    _order = 'sequence, id'

    name = fields.Char('Name', required=True, translate=True)
    sequence = fields.Integer('Sequence', default=20)
    fold = fields.Boolean('Folded in Regulatory Technical File Registry Pipe')
    done = fields.Boolean('Request Done')


class RegulatoryTechnicalFileCreationStage(models.Model):
    _name = 'regulatory.technical.file.creation.stage'
    _description = 'Regulatory Technical File Creation Stage'
    _order = 'sequence, id'

    name = fields.Char('Name', required=True, translate=True)
    sequence = fields.Integer('Sequence', default=20)
    fold = fields.Boolean('Folded in Regulatory Technical File Creation Pipe')
    done = fields.Boolean('Request Done')


class RegulatoryTechnicalFileModificationStage(models.Model):
    _name = 'regulatory.technical.file.modification.stage'
    _description = 'Regulatory Technical File Modification Stage'
    _order = 'sequence, id'

    name = fields.Char('Name', required=True, translate=True)
    sequence = fields.Integer('Sequence', default=20)
    fold = fields.Boolean('Folded in Regulatory Technical File Modification Pipe')
    done = fields.Boolean('Request Done')


class RegulatoryTechnicalFile(models.Model):
    _name = 'regulatory.technical.file'
    _description = 'Regulatory Technical File'
    _inherit = ['mail.thread']

    name = fields.Char(string="Technical File Number", required=True)
    technical_file_name=fields.Char('Technical File Name', required=True)
    description=fields.Text('Description')
    group_id = fields.Many2one('regulatory.technical.file.group', string='Group')
    type_area_id = fields.Many2one('regulatory.technical.file.type.area', string='Type Area')

    _sql_constraints = [
        ('technical_file_model_uniq', 'unique (name)', u'This fact sheet number already exists in our database, enter another number'),
    ]


class RegulatoryTechnicalFileRegistry(models.Model):
    _name = 'regulatory.technical.file.registry'
    _description = 'Regulatory Technical File Registry'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    CATEGORY_SELECTION = [
        ('new', 'New'),
        ('update', 'Update')
    ]

    STATE_SELECTION = [
        ('draft', 'New'),
        ('assigned', 'Assigned'),
        ('review', 'Review of Technical Specifications'),
        ('wait', 'Wait for Factory Documentation'),
        ('appointment', 'Appointment Assigned'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ]

    ENTITY_SELECTION = [
        ('minsa', 'MINSA'),
        ('css', 'CSS'),
    ]

    @api.returns('self')
    def _default_stage(self):
        return self.env['regulatory.technical.file.registry.stage'].search([], limit=1)

    name = fields.Char('#Request:', readonly=True, copy=False, required=True)
    technical_file_id = fields.Many2one('regulatory.technical.file', string='Technical File Number', required=True, track_visibility='onchange')
    technical_file_name = fields.Char(related='technical_file_id.technical_file_name', string='Technical File Name', track_visibility='onchange')
    observation=fields.Text('Observation', track_visibility='onchange')
    sales_team_id = fields.Many2one('crm.team', string='Sales Team', required=True, track_visibility='onchange')
    responsible_id = fields.Many2one('res.users', string='Responsible', track_visibility='onchange', readonly=True)
    models_id = fields.Many2one('equipment.model', string='Models Equipments', required=True, track_visibility='onchange')
    brand_id=fields.Many2one('equipment.brand', related='models_id.brand_id', store=True, string='Brand', track_visibility='onchange')
    stage_id = fields.Many2one('regulatory.technical.file.registry.stage', string='Stage', track_visibility='onchange', default=_default_stage)
    priority = fields.Selection(TICKET_PRIORITY, string='Priority', default='0')
    category = fields.Selection(CATEGORY_SELECTION, 'Category', required=True, default='new', track_visibility='onchange')
    client_id=fields.Many2one('res.partner', string='Factory Contact', track_visibility='onchange', required=True)
    state = fields.Selection(STATE_SELECTION, 'Status', readonly=True, track_visibility='onchange',
        help="When the maintenance order is created the status is set to 'New'.\n\
        If the order is confirmed the status is set to 'Assigned'.\n\
        If the order is confirmed the status is set to 'Review of Technical Specifications'.\n\
        If the stock is available then the status is set to 'Wait for Factory Documentation'.\n\
        If the stock is available then the status is set to 'Appointment Assigned'.\n\
        If the stock is available then the status is set to 'Approved'.\n\
        When the maintenance is over, the status is set to 'Rejected'.", default='draft')
    date_planned = fields.Datetime('Planned Date', default=time.strftime('%Y-%m-%d %H:%M:%S'), track_visibility='onchange')
    location_appointment = fields.Text('Appointment Location')
    fulfill = fields.Boolean('Cumple', track_visibility=True)
    entity = fields.Selection(ENTITY_SELECTION, 'Entity', track_visibility='onchange')

    def action_assign(self):
        self.write({'state': 'assigned'})
        return True

    def action_review(self):
        self.write({'state': 'review'})
        return True

    def action_wait(self):
        stage_id = self.env['regulatory.technical.file.registry.stage'].search([('sequence', '=', '2')], order="sequence asc", limit=1)
        self.write({'state': 'wait'})
        return True

    def action_appointment(self):
        self.write({'state': 'appointment'})
        return True

    def action_approved(self):
        self.write({'state': 'approved'})
        return True

    def action_rejected(self):
        self.write({'state': 'rejected'})
        return True

    @api.multi
    def action_send_mail(self):
        self.ensure_one()
        template_id = self.env.ref('regulatory_issue.mail_template_regulatory_issue_consulting').id
        ctx = {
            'default_model': 'regulatory.technical.file.registry',
            'default_res_id': self.id,
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'custom_layout': 'mail.mail_notification_light',
            'mark_consulting_as_sent': True,
        }
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'target': 'new',
            'context': ctx,
        }

    @api.multi
    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, **kwargs):
        if self.env.context.get('mark_consulting_as_sent'):
            self.filtered(lambda o: o.state == 'review').write({'state': 'wait'})
        return super(RegulatoryTechnicalFileRegistry, self.with_context(mail_post_autofollow=True)).message_post(**kwargs)

    @api.multi
    def action_set_fulfill(self):
        """ Fulfill semantic: """
        return self.write({'fulfill': True})

    @api.multi
    def action_set_fails(self):
        """ Fulfill semantic: """
        return self.write({'fulfill': False})


class RegulatoryTechnicalFileCreation(models.Model):
    _name = 'regulatory.technical.file.creation'
    _description = 'Regulatory Technical File Creation'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.returns('self')
    def _default_stage(self):
        return self.env['regulatory.technical.file.creation.stage'].search([], limit=1)

    name = fields.Char('#Request:', readonly=True, copy=False)
    technical_file_name = fields.Char(string="Proposed Name for the File", required=True, track_visibility='onchange')
    observation=fields.Text('Observation', track_visibility='onchange')
    responsible_id = fields.Many2one('res.users', string='Responsible', track_visibility='onchange', default=lambda self: self.env.user)
    responsible_sales_id = fields.Many2one('res.users', string='Responsible Sale', track_visibility='onchange')
    sales_team_id = fields.Many2one('crm.team', string='Sales Team', track_visibility='onchange')
    models_id = fields.Many2one('equipment.model', string='Model Equipment', track_visibility='onchange')
    brand_id=fields.Many2one('equipment.brand', related='models_id.brand_id', track_visibility='onchange', store=True, string='Brand')
    stage_id = fields.Many2one('regulatory.technical.file.creation.stage', string='Stage', track_visibility='onchange', default=_default_stage)
    priority = fields.Selection(TICKET_PRIORITY, string='Priority', default='0')


class RegulatoryTechnicalFileModification(models.Model):
    _name = 'regulatory.technical.file.modification'
    _description = 'Regulatory Technical File Modification'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    @api.returns('self')
    def _default_stage(self):
        return self.env['regulatory.technical.file.modification.stage'].search([], limit=1)

    name = fields.Char('#Request:', readonly=True, copy=False)
    technical_file_id = fields.Many2one('regulatory.technical.file', string='#Technical File', track_visibility='onchange')
    technical_file_name = fields.Char(related='technical_file_id.technical_file_name', string='Technical File Name', track_visibility='onchange')
    observation=fields.Text('Description', track_visibility='onchange')
    sales_team_id = fields.Many2one('crm.team', string='Sales Team', track_visibility='onchange')
    responsible_id = fields.Many2one('res.users', string='Responsible', track_visibility='onchange', default=lambda self: self.env.user)
    responsible_sales_id = fields.Many2one('res.users', string='Responsible Sale', track_visibility='onchange')
    models_id = fields.Many2one('equipment.model', string='Models Equipments', track_visibility='onchange')
    brand_id=fields.Many2one('equipment.brand', related='models_id.brand_id', store=True, string='Brand', track_visibility='onchange')
    stage_id = fields.Many2one('regulatory.technical.file.modification.stage', string='Stage', track_visibility='onchange', default=_default_stage)
    modification_lines = fields.One2many('regulatory.technical.file.modification.line', 'regulatory_technical_file_modification_id', 'Modification Line', track_visibility='onchange')
    priority = fields.Selection(TICKET_PRIORITY, string='Priority', default='0')


class RegulatoryTechnicalFileModificationLine(models.Model):
    _name = 'regulatory.technical.file.modification.line'
    _description = 'Regulatory Technical File Modification Line'

    name = fields.Char('Point to Change', required=True)
    value = fields.Char('Value', required=True)
    regulatory_technical_file_modification_id = fields.Many2one('regulatory.technical.file.modification', 'Regulatory Technical File Modification')

class RegulatoryTechnicalFileRegistry(models.Model):
    _name = 'regulatory.technical.file.modification.line'
    _description = 'Regulatory Technical File Modification Line'

    name = fields.Char('Point to Change', required=True)
    value = fields.Char('Value', required=True)
    regulatory_technical_file_modification_id = fields.Many2one('regulatory.technical.file.modification', 'Regulatory Technical File Modification')
