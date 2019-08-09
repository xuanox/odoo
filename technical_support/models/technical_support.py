# -*- coding: utf-8 -*-
##############################################################################
#
#    By Rocendo Tejada
#    Copyright (C) 2013-2018 emsa (<http://www.electronicamedica.com>).
#
##############################################################################

import time
from odoo import api, fields, models, _
from odoo import netsvc
import odoo.addons.decimal_precision as dp


class TechnicalSupportRequest(models.Model):
    _name = 'technical_support.request'
    _description = 'Tehcnical Support Request'
    _inherit =  ['mail.thread', 'mail.activity.mixin']

    STATE_SELECTION = [
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('assigned', 'Assigned'),
        ('run', 'In Process'),
        ('done', 'Done'),
        ('reject', 'Rejected'),
        ('cancel', 'Canceled')
    ]

    MAINTENANCE_TYPE_SELECTION = [
        ('pm', 'Preventive'),
        ('cbm', 'Predictive')
    ]

    def _technical_support_count(self):
        order = self.env['technical_support.order']
        for request in self:
            self.technical_support_count = order.search_count([('request_id', '=', request.id)])

    name = fields.Char('Reference', size=64, copy=False)
    state = fields.Selection(STATE_SELECTION, 'Status', readonly=False,
        help="When the maintenance request is created the status is set to 'Draft'.\n\
        If the request is sent the status is set to 'confirm'.\n\
        If the request is confirmed the status is set to 'Execution'.\n\
        If the request is rejected the status is set to 'Rejected'.\n\
        When the maintenance is over, the status is set to 'Done'.", track_visibility='onchange', default='draft', copy=False)
    subject = fields.Char('Subject', size=64, translate=True, required=True, readonly=True, states={'draft': [('readonly', False)]})
    description = fields.Text('Description', readonly=True, states={'draft': [('readonly', False)]})
    reject_reason = fields.Text('Reject Reason')
    detail_confirm_client = fields.Text('Detail Confirm Client')
    detail_confirm_done = fields.Text('Detail Confirm Done')
    requested_date = fields.Datetime('Requested Date', required=True, readonly=True, states={'draft': [('readonly', False)]}, help="Date requested by the customer for maintenance.", default=time.strftime('%Y-%m-%d %H:%M:%S'))
    execution_date = fields.Datetime('Execution Date', required=True, readonly=True, states={'draft':[('readonly',False)],'confirm':[('readonly',False)]}, default=time.strftime('%Y-%m-%d %H:%M:%S'))
    breakdown = fields.Boolean('Breakdown', readonly=True, states={'draft': [('readonly', False)]}, default=False)
    user_id = fields.Many2one('res.users', 'Responsible', track_visibility='onchange', default=lambda self: self._uid, states={'done':[('readonly',True)],'cancel':[('readonly',True)]})
    date_planned = fields.Datetime('Planned Date', required=True, readonly=True, states={'draft':[('readonly',False)]}, default=time.strftime('%Y-%m-%d %H:%M:%S'), track_visibility='onchange')
    detail_new_order = fields.Text('Detail Reason', readonly=True)

    client_id=fields.Many2one('res.partner', string='Client', track_visibility='onchange', required=True, readonly=True, states={'draft': [('readonly', False)]})
    equipment_id = fields.Many2one('equipment.equipment', 'Equipment', required=True, readonly=True, track_visibility='onchange', states={'draft': [('readonly', False)]})
    brand_id=fields.Many2one('equipment.brand', related='equipment_id.brand_id', string='Brand', readonly=True)
    zone_id=fields.Many2one('equipment.zone', related='equipment_id.zone_id', string='Zone', readonly=True)
    model_id=fields.Many2one('equipment.model', related='equipment_id.model_id', string='Model', readonly=True)
    parent_id=fields.Many2one('equipment.equipment', related='equipment_id.parent_id', string='Equipment Relation', readonly=True)
    modality_id=fields.Many2one('equipment.modality', related='equipment_id.modality_id', string='Modality', readonly=True)
    maintenance_type = fields.Selection(MAINTENANCE_TYPE_SELECTION, 'Maintenance Type', required=True, readonly=True, states={'draft': [('readonly', False)]}, default='pm')
    duration = fields.Float('Real Duration', store=True)

    technical_support_count = fields.Integer(compute='_technical_support_count', string='# Reports')

    @api.onchange('requested_date')
    def onchange_requested_date(self):
        self.execution_date = self.requested_date

    @api.onchange('execution_date','state','breakdown')
    def onchange_execution_date(self):
        if self.state == 'draft' and not self.breakdown:
            self.requested_date = self.execution_date

    def action_view_report(self):
        return {
            'domain': "[('request_id','in',[" + ','.join(map(str, self.ids)) + "])]",
            'name': _('Technical Support Orders'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'technical_support.order',
            'type': 'ir.actions.act_window',
            'target': 'current',
        }

    def action_send(self):
        value = {'state': 'confirm'}
        for request in self:
            if request.breakdown:
                value['requested_date'] = time.strftime('%Y-%m-%d %H:%M:%S')
            request.write(value)

    def action_confirm(self):
        order = self.env['technical_support.order']
        order_id = False
        for request in self:
            order_id = order.create({
                'date_planned':request.requested_date,
                'date_scheduled':request.requested_date,
                'date_execution':request.requested_date,
                'origin': request.name,
                'user_id': request.user_id.id,
                'state': 'draft',
                'maintenance_type': request.maintenance_type,
                'equipment_id': request.equipment_id.id,
                'description': request.subject,
                'problem_description': request.description,
                'request_id': request.id,
            })
        self.write({'state': 'assigned'})
        return order_id.id

    def action_done(self):
        self.write({'state': 'done', 'execution_date': time.strftime('%Y-%m-%d %H:%M:%S')})
        return True

    def action_reject(self):
        self.write({'state': 'reject', 'execution_date': time.strftime('%Y-%m-%d %H:%M:%S')})
        return True

    def action_confirm_client(self):
        self.write({'state': 'confirm'})
        return True

    def action_cancel(self):
        self.write({'state': 'cancel', 'execution_date': time.strftime('%Y-%m-%d %H:%M:%S')})
        return True

    def action_draft(self):
        self.write({'state': 'draft'})
        return True

    @api.model
    def create(self, vals):
        if vals.get('name','/')=='/':
            vals['name'] = self.env['ir.sequence'].next_by_code('technical_support.request') or '/'
        return super(TechnicalSupportRequest, self).create(vals)
