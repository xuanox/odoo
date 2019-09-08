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
        ('review', 'Review'),
        ('wait', 'Consult'),
        ('appointment', 'Scheduled'),
        ('waiting', 'Waiting'),
        ('correct', 'Correct'),
        ('done', 'Completed')
    ]

    ENTITY_SELECTION = [
        ('minsa', 'MINSA'),
        ('css', 'CSS'),
    ]

    name = fields.Char('#Request:', readonly=True, copy=False, required=True, default='New')
    technical_file_id = fields.Many2one('regulatory.technical.file', string='Technical File Number', required=True, track_visibility='onchange')
    technical_file_name = fields.Char(related='technical_file_id.technical_file_name', string='Technical File Name', track_visibility='onchange')
    observation=fields.Text('Observation', track_visibility='onchange')
    team_id = fields.Many2one('crm.team', string='Sales Team', required=True, track_visibility='onchange', default=lambda self: self.env['crm.team'].sudo()._get_default_team_id(user_id=self.env.uid))
    user_id = fields.Many2one('res.users', string='Responsible', required=True, track_visibility='onchange', default=lambda self: self.env.user)
    responsible_sales_id = fields.Many2one('res.users', string='Sales Person', track_visibility='onchange', readonly=True)
    responsible_team_lider_id = fields.Many2one('res.users', related='team_id.user_id', string='Team Lider', track_visibility='onchange')
    models_id = fields.Many2one('equipment.model', string='Models Equipments', required=True, track_visibility='onchange')
    brand_id=fields.Many2one('equipment.brand', related='models_id.brand_id', store=True, string='Brand', track_visibility='onchange')
    priority = fields.Selection(TICKET_PRIORITY, string='Priority', default='0')
    category = fields.Selection(CATEGORY_SELECTION, 'Category', required=True, track_visibility='onchange')
    contact_id=fields.Many2one('res.partner', string='Factory Contact', track_visibility='onchange', required=True)
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
    is_won = fields.Boolean('Cumple', track_visibility=True)
    is_lost = fields.Boolean('No Cumple', track_visibility=True)
    is_approved = fields.Boolean('Approved', track_visibility=True)
    is_rejected = fields.Boolean('Rejected', track_visibility=True)
    lost_reason = fields.Many2one('regulatory.technical.file.registry.lost.reason', string='Porque no cumple', index=True, track_visibility='onchange')
    reject_reason = fields.Many2one('regulatory.technical.file.registry.reject.reason', string='Reject Reason', index=True, track_visibility='onchange')
    entity = fields.Selection(ENTITY_SELECTION, 'Entity', track_visibility='onchange')
    pending_documentation_ids=fields.One2many('regulatory.technical.file.registry.pending.documentation','registry_id', string='Pending Documentation', readonly=True, states={'review':[('readonly',False)],'wait':[('readonly',False)]})
    entity_id = fields.Many2one('regulatory.entity', string='Entity', track_visibility='onchange')
    location_homologation=fields.Text(related='entity_id.description', string='Homologation Location', readonly=True, track_visibility='onchange')
    tfc_id = fields.Many2one('regulatory.technical.file.creation', string='TFC')
    tfm_id = fields.Many2one('regulatory.technical.file.modification', string='TFM')

    @api.model
    def _onchange_user_values(self, user_id):
        if not user_id:
            return {}
        if user_id and self._context.get('team_id'):
            team = self.env['crm.team'].browse(self._context['team_id'])
            if user_id in team.member_ids.ids:
                return {}
        team_id = self.env['crm.team']._get_default_team_id(user_id=user_id)
        return {'team_id': team_id}

    @api.onchange('user_id')
    def _onchange_user_id(self):
        if self.user_id.sale_team_id:
            values = self._onchange_user_values(self.user_id.id)
            self.update(values)

    @api.onchange('entity')
    def _onchange_entity(self):
        if self.entity == 'minsa':
            location_appointment = "Dirección Nacional de Dispositivos Médicos."
        if self.entity == 'css':
            location_appointment = "Departamento Nacional de Evaluación y Gestión de Tecnología Sanitaria."

    def action_assign(self):
        self.write({'state': 'assigned'})
        return True

    def action_review(self):
        self.write({'state': 'review'})
        return True

    def action_wait(self):
        self.write({'state': 'wait'})
        return True

    def action_appointment(self):
        self.write({'state': 'appointment'})
        return True

    def action_appointment_approved(self):
        self.write({'state': 'waiting'})
        self.write({'is_approved': True})
        return True

    def action_approved(self):
        self.write({'state': 'done'})
        return True

    def action_rejected(self):
        self.write({'state': 'correct'})
        return True

    def action_appointment_rejected(self):
        self.write({'state': 'correct'})
        self.write({'is_rejected': True})
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
        return self.write({'is_won': True})

    @api.multi
    def action_set_fails(self):
        """ Fulfill semantic: """
        return self.write({'is_lost': True})

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('regulatory.technical.file.registry') or '/'
        return super(RegulatoryTechnicalFileRegistry, self).create(vals)


class RegulatoryTechnicalFileRegistryLostReason(models.Model):
    _name = 'regulatory.technical.file.registry.lost.reason'
    _description = 'Regulatory Technical File Registry Lost Reason'

    name = fields.Char(string="Reason", required=True)
    description=fields.Text('Description')


class RegulatoryTechnicalFileRegistryRejectReason(models.Model):
    _name = 'regulatory.technical.file.registry.reject.reason'
    _description = 'Regulatory Technical File Registry Reject Reason'

    name = fields.Char(string="Reason", required=True)
    description=fields.Text('Description')


class RegulatoryTechnicalFileRegistryPendingDocumentation(models.Model):
    _name = 'regulatory.technical.file.registry.pending.documentation'
    _description = 'Regulatory Technical File Registry Pending Documentation'

    CHOICE_STATUS = [
        ('done','Done'),
        ('notdone','Not Done')]

    name = fields.Char('Description', required=True)
    legal_documentation_id=fields.Many2one('regulatory.legal.documentation', string='Documentation', required=True)
    registry_id=fields.Many2one('regulatory.technical.file.registry', string='Registry')
    status=fields.Selection(CHOICE_STATUS, string="Status")
    done = fields.Boolean('Done')
    note = fields.Text('Note')

    @api.onchange('legal_documentation_id')
    def onchange_legal_documentation_id(self):
        self.name = self.legal_documentation_id.display_name
