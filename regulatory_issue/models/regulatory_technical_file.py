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

from datetime import date, datetime, timedelta
from odoo import models, fields, api
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

    @api.returns('self')
    def _default_stage(self):
        return self.env['regulatory.technical.file.registry.stage'].search([], limit=1)

    name = fields.Char('#Request:', readonly=True, copy=False, required=True)
    technical_file_id = fields.Many2one('regulatory.technical.file', string='Technical File Number', track_visibility='onchange')
    technical_file_name = fields.Char(related='technical_file_id.technical_file_name', string='Technical File Name', track_visibility='onchange')
    observation=fields.Text('Observation', track_visibility='onchange')
    sales_team_id = fields.Many2one('crm.team', string='Sales Team', track_visibility='onchange')
    responsible_id = fields.Many2one('res.users', string='Responsible', track_visibility='onchange', default=lambda self: self.env.user)
    models_id = fields.Many2one('equipment.model', string='Models Equipments', track_visibility='onchange')
    brand_id=fields.Many2one('equipment.brand', related='models_id.brand_id', store=True, string='Brand', track_visibility='onchange')
    stage_id = fields.Many2one('regulatory.technical.file.registry.stage', string='Stage', track_visibility='onchange', default=_default_stage)
    priority = fields.Selection(TICKET_PRIORITY, string='Priority', default='0')
    category = fields.Selection(CATEGORY_SELECTION, 'Category', required=True, default='cm', track_visibility='onchange')


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
