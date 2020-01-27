# -*- coding: utf-8 -*-
###################################################################################
#
#    Electrónica Médica.
#    Copyright (C) 2019-TODAY Electrónica Médica (<https://www.electronicamedica.com>).
#
#    Author: Aldhair Atencio (<https://www.electronicamedica.com>)
#
###################################################################################
import time
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo import netsvc
import odoo.addons.decimal_precision as dp
from datetime import date, datetime, timedelta
from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError

TICKET_PRIORITY = [
    ('0', 'Normal'),
    ('1', 'Bajar prioridad'),
    ('2', 'Alta prioridad'),
    ('3', 'Urgente'),
]

class messenger_service_tags(models.Model):
   _description = 'Messenger Service Tags'
   _name = 'messenger.service.tags'

   name = fields.Char('Tag', required=True, translate=True)
   equipment_ids = fields.Many2many('messenger.service.dashboard', id1='category_id', id2='equipment_id', string='Equipments')


class MessengerServiceDashboard(models.Model):
    _name = 'messenger.service.dashboard'
    _description = 'Messenger Service Dashboard'
    _order = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    STATE_SELECTION = [
        ('draft', 'Nuevo'),
        ('asign', 'Agendado'),
        ('run', 'En proceso'),
        ('done', 'Realizado'),
        ('cancel', 'Cancelado')
    ]
    SERVICE_TYPE_SELECTION = [
        ('entre', 'Entrega'),
        ('retir', 'Retiro'),
        ('busq', 'Búsqueda de Firma'),
        ('licit', 'Licitación'),
        ('equip', 'Entrega de Equipo'),
        ('otro', 'Otros')
        ]

    service_type = fields.Selection(SERVICE_TYPE_SELECTION, 'Tipo de mensajería', required=True, states={'done':[('readonly',True)],'cancel':[('readonly',True)]}, default='entre', track_visibility='onchange')
    state=fields.Selection(STATE_SELECTION, 'Estado', readonly=False, track_visibility='onchange', help="", default='draft', copy=False)
    name=fields.Char(string="Solicitud", required=False)
    user_id=fields.Many2one('res.users', string='Responsable', index=True, track_visibility='onchange', default=lambda self: self._uid)
    assigned_id=fields.Many2one('res.users', string='Asignado', index=True, track_visibility='onchange', default=lambda self: self.env.user)
    client_id=fields.Many2one('res.partner', string='Cliente', required=True, track_visibility='onchange')
    description=fields.Text('Indicaciones especiales', required=True)
    direction=fields.Text('Dirección destino', required=True)
    department=fields.Char(string="Departamento Destino", required=True)
    company_id= fields.Many2one('res.company', 'Company', required=True, index=True, default=lambda self: self.env.user.company_id.id)#
    date_planned=fields.Datetime('Fecha de Entrega', track_visibility='onchange')
    date_end = fields.Datetime(string='Fecha límite', required=True,track_visibility='onchange', states={'done': [('readonly', True)]})
    create_date=fields.Datetime('Fecha de creación', required=True, default=time.strftime('%Y-%m-%d %H:%M:%S'), track_visibility='onchange')
    category_ids = fields.Many2many('messenger.service.tags', id1='equipment_id', id2='category_id', string='Etiquetas')
    priority = fields.Selection(TICKET_PRIORITY, string='Prioridad', default='0')


    def action_assigned(self):
        self.write({'state': 'asign'})
        return True

    def action_reassigned(self):
        self.write({'state': 'asign'})
        return True

    def action_replanned(self):
        self.write({'state': 'asign'})
        return True

    def action_run(self):
        self.write({'state': 'run'})
        return True

    def action_done(self):
        self.write({'state': 'done'})
        return True

    def action_canceled(self):
        self.write({'state': 'cancel'})
        return True

    @api.model
    def create(self, vals):
        if vals.get('name','/')=='/':
            vals['name'] = self.env['ir.sequence'].next_by_code('messenger_service.request') or '/'
        return super(MessengerServiceDashboard, self).create(vals)
