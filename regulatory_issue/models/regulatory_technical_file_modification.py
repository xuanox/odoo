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

class RegulatoryTechnicalFileModificationStage(models.Model):
    _name = 'regulatory.technical.file.modification.stage'
    _description = 'Regulatory Technical File Modification Stage'
    _order = 'sequence, id'

    name = fields.Char('Name', required=True, translate=True)
    sequence = fields.Integer('Sequence', default=20)
    fold = fields.Boolean('Folded in Regulatory Technical File Modification Pipe')
    done = fields.Boolean('Request Done')


class RegulatoryTechnicalFileModification(models.Model):
    _name = 'regulatory.technical.file.modification'
    _description = 'Regulatory Technical File Modification'
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
        return self.env['regulatory.technical.file.modification.stage'].search([], limit=1)

    name = fields.Char('#Request:', readonly=True, copy=False, required=True, default='New')
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
    state = fields.Selection(STATE_SELECTION, 'Status', readonly=True, track_visibility='onchange',
        help="When the maintenance order is created the status is set to 'New'.\n\
        If the order is Assigned the status is set to 'Assigned'.\n\
        If the order is Process the status is set to 'Process'.\n\
        If the order is Homologation the status is set to 'Homologation'.\n\
        If the stock is Completed then the status is set to 'Completed'.\n\
        When the request is over, the status is set to 'Rejected'.", default='draft')
    entity = fields.Selection(ENTITY_SELECTION, 'Entity', track_visibility='onchange')
    entity_id = fields.Many2one('regulatory.entity', string='Entity', track_visibility='onchange')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('regulatory.technical.file.modification') or '/'
        return super(RegulatoryTechnicalFileModification, self).create(vals)

class RegulatoryTechnicalFileModificationLine(models.Model):
    _name = 'regulatory.technical.file.modification.line'
    _description = 'Regulatory Technical File Modification Line'

    name = fields.Char('Point to Change', required=True)
    value = fields.Char('Value', required=True)
    regulatory_technical_file_modification_id = fields.Many2one('regulatory.technical.file.modification', 'Regulatory Technical File Modification')
