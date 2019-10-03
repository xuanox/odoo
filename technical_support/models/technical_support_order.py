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


class TechnicalSupportOrder(models.Model):
    _name = 'technical_support.order'
    _description = 'Technical Support Order'
    _inherit =  ['mail.thread', 'mail.activity.mixin']
    _order = 'name desc'

    STATE_SELECTION = [
        ('draft', 'DRAFT'),
        ('released', 'WAITING PARTS'),
        ('consulting', 'CONSULTING FACTORY'),
        ('ready', 'IN PROCESS'),
        ('done', 'DONE'),
        ('cancel', 'CANCELED')
    ]

    MAINTENANCE_TYPE_SELECTION = [
        ('pm', 'Preventive'),
        ('cm', 'Corrective'),
        ('in', 'Instalación'),
        ('cbm', 'Predictive'),
        ('din', 'Uninstall'),
        ('fco', 'FCO')
    ]

    @api.multi
    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'state' in init_values and self.state == 'ready':
            return 'technical_support.mt_order_confirmed'
        return super(TechnicalSupportOrder, self)._track_subtype(init_values)

    name = fields.Char('Reference', size=64)
    description = fields.Char(related='ticket_id.name', string='Description', size=64, readonly=True, track_visibility='onchange')
    origin = fields.Char('Source Document', size=64, states={'done':[('readonly',True)],'cancel':[('readonly',True)]},
        help="Reference of the document that generated this Technical Support Order.", track_visibility='onchange')
    state = fields.Selection(STATE_SELECTION, 'Status', readonly=True, track_visibility='onchange',
        help="When the maintenance order is created the status is set to 'Draft'.\n\
        If the order is confirmed the status is set to 'Waiting Parts'.\n\
        If the order is confirmed the status is set to 'Consulting Factory'.\n\
        If the stock is available then the status is set to 'Ready to Maintenance'.\n\
        When the maintenance is over, the status is set to 'Done'.", default='draft')
    maintenance_type = fields.Selection(MAINTENANCE_TYPE_SELECTION, 'Maintenance Type', required=True, states={'done':[('readonly',True)],'cancel':[('readonly',True)]}, default='cm', track_visibility='onchange')
    ticket_type_id = fields.Many2one('helpdesk.ticket.type', string="Ticket Type", track_visibility='onchange', states={'done':[('readonly',True)],'cancel':[('readonly',True)]})

    date_planned = fields.Datetime('Planned Date', required=True, readonly=True, states={'draft':[('readonly',False)]}, default=time.strftime('%Y-%m-%d %H:%M:%S'), track_visibility='onchange')
    date_scheduled = fields.Datetime('Start Date', required=True, states={'done':[('readonly',True)],'cancel':[('readonly',True)]}, default=time.strftime('%Y-%m-%d %H:%M:%S'), track_visibility='onchange')
    date_execution = fields.Datetime('Execution Date', required=True, states={'done':[('readonly',True)],'cancel':[('readonly',True)],'ready':[('readonly',True)]}, default=time.strftime('%Y-%m-%d %H:%M:%S'), track_visibility='onchange')
    date_finish = fields.Datetime('Finish Date', required=True, states={'done':[('readonly',True)],'cancel':[('readonly',True)]}, default=time.strftime('%Y-%m-%d %H:%M:%S'), track_visibility='onchange')

    tools_description = fields.Text('Tools Description', states={'done':[('readonly',True)],'cancel':[('readonly',True)]})
    labor_description = fields.Text('Labor Description', states={'done':[('readonly',True)],'cancel':[('readonly',True)]})
    operations_description = fields.Text('Operations Description', states={'done':[('readonly',True)],'cancel':[('readonly',True)]})
    documentation_description = fields.Text('Documentation Description', states={'done':[('readonly',True)],'cancel':[('readonly',True)]})
    problem_description = fields.Text(related='ticket_id.description', string='Problem Description', readonly=True, store=True, track_visibility='onchange')

    ticket_id = fields.Many2one('helpdesk.ticket', string='Ticket', track_visibility='onchange', states={'done':[('readonly',True)],'cancel':[('readonly',True)]})
    task_id = fields.Many2one('technical_support.task', 'Task', states={'done':[('readonly',True)],'cancel':[('readonly',True)]}, domain="[('model_id', '=', model_id)]")
    equipment_id = fields.Many2one('equipment.equipment', string='Equipment', required=True, readonly=True, states={'draft':[('readonly',False)]})
    user_id = fields.Many2one('res.users', 'Responsible', track_visibility='onchange', default=lambda self: self._uid, states={'done':[('readonly',True)],'cancel':[('readonly',True)]})
    company_id = fields.Many2one('res.company','Company', required=True, readonly=True, states={'draft':[('readonly',False)]}, default=lambda self: self.env['res.company']._company_default_get('technical_support.order'))
    procurement_group_id = fields.Many2one('procurement.group', 'Procurement group', copy=False)
    category_ids = fields.Many2many(related='equipment_id.category_ids', string='equipment Category', readonly=True)
    wo_id = fields.Many2one('technical_support.workorder', 'Work Order', ondelete='cascade')
    request_id = fields.Many2one('technical_support.request', 'Request', ondelete='cascade')
    client_id=fields.Many2one('res.partner', related='equipment_id.client_id', string='Client', store=True, readonly=True)
    brand_id=fields.Many2one('equipment.brand', related='equipment_id.brand_id', string='Brand', readonly=True)
    zone_id=fields.Many2one('equipment.zone', related='equipment_id.zone_id', string='Zone', readonly=True)
    model_id=fields.Many2one('equipment.model', related='equipment_id.model_id', string='Model', store=True, readonly=True)
    parent_id=fields.Many2one('equipment.equipment', related='equipment_id.parent_id', string='Equipment Relation', readonly=True)
    modality_id=fields.Many2one('equipment.modality', related='equipment_id.modality_id', string='Modality', store=True, readonly=True)
    order_id = fields.Many2one('technical_support.checklist.history', string='Control List')
    equipment_state_id = fields.Many2one('equipment.state', related='equipment_id.maintenance_state_id', string='Equipment State', domain=[('team','=','3')], readonly=True, store=True)

    parts_lines = fields.One2many('technical_support.order.parts.line', 'maintenance_id', 'Planned Parts', track_visibility='onchange', states={'done':[('readonly',True)],'cancel':[('readonly',True)]})
    assets_lines = fields.One2many('technical_support.order.assets.line', 'maintenance_id', 'Planned Tools', track_visibility='onchange', states={'done':[('readonly',True)], 'cancel':[('readonly',True)]})
    checklist_lines = fields.One2many('technical_support.order.checklist.line', 'maintenance_id', 'CheckList', track_visibility='onchange', states={'done':[('readonly',True)],'cancel':[('readonly',True)]})
    signature_lines = fields.One2many('technical_support.order.signature.line', 'maintenance_id', 'Users', track_visibility='onchange')
    signature_client_lines = fields.One2many('technical_support.order.signature.client.line', 'maintenance_id', 'Clients', track_visibility='onchange')

    serial=fields.Char(related='equipment_id.serial', string='Serial', readonly=True)
    equipment_number=fields.Char(related='equipment_id.equipment_number', string='N° de Equipo', readonly=True)
    location=fields.Char(related='equipment_id.location', string='Location', readonly=True)

    active = fields.Boolean(default=True)
    signature = fields.Binary('Signature', help='Signature received through the portal.', copy=False, attachment=True)
    require_signature = fields.Boolean('Online Signature', readonly=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        help='Request a online signature to the customer in order to confirm orders automatically.')
    signed_by = fields.Char('Signed by', help='Name of the person that signed the SO.', copy=False)
    wait_time= fields.Float(help="Wait Time in hours and minutes.", track_visibility='onchange')
    transportation_time= fields.Float(help="Transportation Time in hours and minutes.", track_visibility='onchange')
    duration = fields.Float('Real Duration', store=True)

    detail_cause = fields.Text('Detail Causa', readonly=True)
    cause_reason = fields.Many2one('helpdesk.ticket.cause.reason', string='cause Reason', index=True, track_visibility='onchange')
    remote = fields.Boolean('Remote Attention', copy=False)
    close_order = fields.Boolean('Close Order Only', copy=False)
    close_ticket = fields.Boolean('Close Order and Ticket', copy=False)
    observation = fields.Boolean('Observation', copy=False)

    @api.onchange('equipment_id','maintenance_type')
    def onchange_equipment(self):
        if self.equipment_id:
            self.model_id = self.equipment_id.model_id
        return {'domain': {'task_id': [('model_id', 'in', self.model_id.ids),('maintenance_type','=',self.maintenance_type)]}}

    @api.onchange('date_planned')
    def onchange_planned_date(self):
        self.date_scheduled = self.date_planned

    @api.onchange('date_scheduled')
    def onchange_scheduled_date(self):
        self.date_execution = self.date_scheduled

#    @api.onchange('date_execution')
#    def onchange_execution_date(self):
#        if self.state == 'draft':
#            self.date_planned = self.date_execution
#        else:
#            self.date_scheduled = self.date_execution

    @api.onchange('task_id')
    def onchange_task(self):
        task = self.task_id
        new_checklist_lines = []
        for line in task.checklist_lines:
            new_checklist_lines.append([0,0,{
                'name': line.name,
                'question_id': line.question_id.id,
                'answer': line.answer,
                }])
        self.checklist_lines = new_checklist_lines
        self.description = task.name
        self.tools_description = task.tools_description
        self.labor_description = task.labor_description
        self.operations_description = task.operations_description
        self.documentation_description = task.documentation_description

    @api.onchange('ticket_id')
    def onchange_ticket(self):
        self.equipment_id = self.ticket_id.equipment_id
        self.user_id = self.ticket_id.user_id

    def test_ready(self):
        res = True
        for order in self:
            if order.parts_lines and order.procurement_group_id:
                states = []
                for procurement in order.procurement_group_id.procurement_ids:
                    states += [move.state != 'assigned' for move in procurement.move_ids if move.location_dest_id.id == order.equipment_id.property_stock_equipment.id]
                if any(states) or len(states) == 0: res = False
        return res

    def test_if_parts(self):
        res = True
        for order in self:
            order.parts_lines.write({'state': 'released'})
            if not order.parts_lines:
                res = False
        return res

    # ACTIONS
    def action_confirm(self):
        self.write({'state': 'ready'})
        self.ticket_id.write({'stage_id': 2})
        self.request_id.write({'state': 'run'})
        return True

    def action_ready(self):
        self.write({'state': 'ready'})
        return True

    def action_done(self):
        self.request_id.write({'state': 'done'})
        for order in self:
            if order.test_if_parts():
                order.write({'state': 'done', 'date_execution': time.strftime('%Y-%m-%d %H:%M:%S')})
            else:
                order.write({'state': 'done', 'date_execution': time.strftime('%Y-%m-%d %H:%M:%S')})
        return 0

    def action_cancel(self):
        self.write({'state': 'cancel'})
        return True

    def ticket_done(self):
        for order in self:
            if order.ticket_id:
                order.ticket_id.write({'stage_id': 3})
                order.ticket_id.remote = order.remote
                order.ticket_id.observation = order.observation
                order.ticket_id.detail_cause= order.detail_cause
                order.ticket_id.cause_reason= order.cause_reason.id
        return True

    def action_change_equipment_ticket(self):
        for order in self:
            if order.ticket_id:
                order.ticket_id.equipment_id = order.equipment_id
        return True

    def action_change_equipment_tsr(self):
        for order in self:
            if order.request_id:
                order.request_id.equipment_id = order.equipment_id
        return True

    def _track_subtype(self, init_values):
        # init_values contains the modified fields' values before the changes
        #
        # the applied values can be accessed on the record as they are already
        # in cache
        self.ensure_one()
        if 'state' in init_values and self.state == 'done':
            return 'technical_support.mt_state_change'  # Full external id
        return super(TechnicalSupportOrder, self)._track_subtype(init_values)

    # CRUD
    @api.model
    def create(self, vals):
        if vals.get('name','/')=='/':
            vals['name'] = self.env['ir.sequence'].next_by_code('technical_support.order') or '/'
        request = super(TechnicalSupportOrder, self).create(vals)
        request.activity_update()
        return request

    @api.multi
    def write(self, vals):
        if vals.get('date_execution') and not vals.get('state'):
            # constraint for calendar view
            for order in self:
                if order.state == 'draft':
                    vals['date_planned'] = vals['date_execution']
                    vals['date_scheduled'] = vals['date_execution']
                elif order.state in ('released','ready'):
                    vals['date_scheduled'] = vals['date_execution']
                else: del vals['date_execution']
        res = super(TechnicalSupportOrder, self).write(vals)
        if 'state' in vals:
            self.filtered(lambda m: m.state == 'ready')
            self.activity_feedback(['technical_support.mail_act_technical_support_order'])
        if vals.get('user_id') or vals.get('date_planned'):
            self.activity_update()
        if vals.get('equipment_id'):
            # need to change description of activity also so unlink old and create new activity
            self.activity_unlink(['technical_support.mail_act_technical_support_order'])
            self.activity_update()
        return res

    def activity_update(self):
        """ Update maintenance activities based on current record set state.
        It reschedule, unlink or create maintenance request activities. """
        self.filtered(lambda request: not request.date_planned).activity_unlink(['technical_support.mail_act_technical_support_order'])
        for request in self.filtered(lambda request: request.date_planned):
            date_dl = fields.Datetime.from_string(request.date_planned).date()
            updated = request.activity_reschedule(
                ['technical_support.mail_act_technical_support_order'],
                date_deadline=date_dl,
                new_user_id=request.user_id.id or self.env.uid)
            if not updated:
                if request.equipment_id:
                    note = _('Request planned for <a href="#" data-oe-model="%s" data-oe-id="%s">%s</a>') % (
                        request.equipment_id._name, request.equipment_id.id, request.equipment_id.display_name)
                else:
                    note = False
                request.activity_schedule(
                    'technical_support.mail_act_technical_support_order',
                    fields.Datetime.from_string(request.date_planned).date(),
                    note=note, user_id=request.user_id.id or self.env.uid)


    @api.multi
    def action_send_mail(self):
        self.ensure_one()
        template_id = self.env.ref('technical_support.mail_template_technical_support_consulting').id
        ctx = {
            'default_model': 'technical_support.order',
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
            self.filtered(lambda o: o.state == 'ready').write({'state': 'consulting'})
        return super(TechnicalSupportOrder, self.with_context(mail_post_autofollow=True)).message_post(**kwargs)


class TechnicalSupportOrderPartsLine(models.Model):
    _name = 'technical_support.order.parts.line'
    _description = 'Maintenance Planned Parts'
    _inherit =  ['mail.thread', 'mail.activity.mixin']

    STATE_SELECTION = [
        ('draft', 'Draft'),
        ('released', 'Registered Part'),
        ('approved', 'Approved Part'),
        ('requested_part', 'Requested Part'),
        ('received_part', 'Received Part'),
        ('ready', 'Available'),
        ('done', 'Installed'),
        ('cancel', 'Canceled')
    ]

    CHOICE_MAINTASK = [
        ('done','Done'),
        ('notdone','Not Done'),
        ('na','N/A')]

    name = fields.Char('Description', size=64)
    parts_id = fields.Many2one('product.product', 'Parts', required=True, track_visibility='onchange', readonly=True, states={'draft':[('readonly',False)]})
    parts_qty = fields.Float('Quantity', digits=dp.get_precision('Product Unit of Measure'), track_visibility='onchange', readonly=True, states={'draft':[('readonly',False)]}, required=True, default=1.0)
    parts_uom = fields.Many2one('uom.uom', 'Unit of Measure', track_visibility='onchange', required=True, readonly=True, states={'draft':[('readonly',False)]})
    maintenance_id = fields.Many2one('technical_support.order', 'Maintenance Order')
    state = fields.Selection(STATE_SELECTION, 'Status', track_visibility='onchange', readonly=True, states={'ready':[('readonly',False)]},
        help="When the maintenance order is created the status is set to 'Draft'.\n\
        If the order is confirmed the status is set to 'Waiting Parts'.\n\
        If the stock is available then the status is set to 'Ready to Maintenance'.\n\
        When the maintenance is over, the status is set to 'Done'.", default='draft')
    answer=fields.Selection(CHOICE_MAINTASK, u"State")
    ticket_id = fields.Many2one('helpdesk.ticket', 'Ticket')
    part_line_id = fields.Many2one('part.line', 'Part Line')

    def unlink(self):
        self.write({'maintenance_id': False})
        return True

    @api.model
    def create(self, values):
        ids = self.search([('maintenance_id','=',values['maintenance_id']),('parts_id','=',values['parts_id'])])
        if len(ids)>0:
            values['parts_qty'] = ids[0].parts_qty + values['parts_qty']
            ids[0].write(values)
            return ids[0]
        ids = self.search([('maintenance_id','=',False)])
        if len(ids)>0:
            ids[0].write(values)
            return ids[0]
        return super(TechnicalSupportOrderPartsLine, self).create(values)

class TechnicalSupportOrderChecklistLine(models.Model):
    _name = 'technical_support.order.checklist.line'
    _description = 'Maintenance Planned Checklist'

    CHOICE_MAINTASK = [
        ('done','Done'),
        ('notdone','Not Done'),
        ('na','N/A')]

    name = fields.Char('Description', size=64)
    question_id=fields.Many2one('technical_support.question', u'Question', required=True)
    answer=fields.Selection(CHOICE_MAINTASK, u"State")
    maintenance_id = fields.Many2one('technical_support.order', 'Maintenance Order')

    def unlink(self):
        self.write({'maintenance_id': False})
        return True

class TechnicalSupportTask(models.Model):
    """
    Maintenance Tasks (Template for order)
    """
    _name = 'technical_support.task'
    _description = 'Maintenance Task'

    MAINTENANCE_TYPE_SELECTION = [
        ('pm', 'Preventive'),
        ('pd', 'Predictive'),
        ('in', 'Install'),
        ('un', 'Uninstall'),
        ('fco', 'FCO')
    ]

    name = fields.Char('Description', size=64, required=True, translate=True)
    active = fields.Boolean('Active', default=True)
    maintenance_type = fields.Selection(MAINTENANCE_TYPE_SELECTION, 'Maintenance Type', required=True, default='pm')
    ticket_type_id = fields.Many2one('helpdesk.ticket.type', string="Ticket Type")

    category_id = fields.Many2one('equipment.category', 'Category', ondelete='restrict', required=True)
    model_id = fields.Many2one('equipment.model', 'Model', ondelete='restrict', required=True)

    checklist_lines = fields.One2many('technical_support.task.checklist.line', 'task_id', 'CheckList')

    tools_description = fields.Text('Tools Description')
    labor_description = fields.Text('Labor Description')
    operations_description = fields.Text('Operations Description')
    documentation_description = fields.Text('Documentation Description')

class TechnicalSupportTaskPartsLine(models.Model):
    _name = 'technical_support.task.parts.line'
    _description = 'Maintenance Planned Parts'

    name = fields.Char('Description', size=64)
    parts_id = fields.Many2one('product.product', 'Parts', required=True)
    parts_qty = fields.Float('Quantity', digits=dp.get_precision('Product Unit of Measure'), required=True, default=1.0)
    parts_uom = fields.Many2one('uom.uom', 'Unit of Measure', required=True)
    task_id = fields.Many2one('technical_support.task', 'Maintenance Task')

    @api.onchange('parts_id')
    def onchange_parts(self):
        self.parts_uom = self.parts_id.uom_id.id

    def unlink(self):
        self.write({'task_id': False})
        return True

    @api.model
    def create(self, values):
        ids = self.search([('task_id','=',values['task_id']),('parts_id','=',values['parts_id'])])
        if len(ids)>0:
            values['parts_qty'] = ids[0].parts_qty + values['parts_qty']
            ids[0].write(values)
            return ids[0]
        ids = self.search([('task_id','=',False)])
        if len(ids)>0:
            ids[0].write(values)
            return ids[0]
        return super(TechnicalSupportTaskPartsLine, self).create(values)

class TechnicalSupportTaskChecklistLine(models.Model):
    _name = 'technical_support.task.checklist.line'
    _description = 'Maintenance Planned CheckList'

    CHOICE_MAINTASK = [
        ('done','Done'),
        ('notdone','Not Done'),
        ('na','N/A')]

    name = fields.Char('Description', size=64)
    question_id=fields.Many2one('technical_support.question', u'Question', required=True)
    answer=fields.Selection(CHOICE_MAINTASK, u"State")
    task_id = fields.Many2one('technical_support.task', 'Maintenance Task')

    def unlink(self):
        self.write({'task_id': False})
        return True

class TechnicalSupportOrderAssetsLine(models.Model):
    _name = 'technical_support.order.assets.line'
    _description = 'Maintenance Planned Assets'

    name = fields.Char('Description', size=64)
    assets_id = fields.Many2one('asset.asset', 'Assets', required=True)
    maintenance_id = fields.Many2one('technical_support.order', 'Maintenance Order')
    maintenance_state_id = fields.Many2one('asset.state', related='assets_id.maintenance_state_id', string='State')

class TechnicalSupportChecklistHistory(models.Model):
    _name="technical_support.checklist.history"
    _description= "Checklist History"
    _inherit = ['mail.thread']
    _order = 'name desc'

    @api.onchange('checklist_id')
    def onchange_checklist_id(self):
        if self.checklist_id:
            liste = self.env['technical_support.question'].search([('checklist_id', '=', self.id)])
            #enrs = self.env['technical_support.question'].name_get(liste)
            res = []
            for id, name in liste:
                obj = {'name': name}
                res.append(obj)
            return {'value':{'answers_ids': res}}


    @api.one
    def action_done(self):
        self.state='done'
        return True

    @api.one
    def action_confirmed(self):
        self.state='confirmed'
        return True

    @api.one
    def action_draft(self):
        self.state='draft'
        return True


    name=fields.Char("Nom", default=lambda x: x.env['ir.sequence'].get('technical_support.checklist.history'))
    checklist_id=fields.Many2one('technical_support.checklist', 'Control List')
    answers_ids=fields.One2many("technical_support.answer.history","checklist_history_id","Answers")
    ot_ids=fields.One2many('technical_support.order','order_id',"Order")
    date_planned=fields.Datetime("Scheduled Date")
    date_end=fields.Datetime("End Date")
    models_id=fields.Many2one('equipment.model', u'Model')
    user_id=fields.Many2one('res.users', 'Responsible')
    state=fields.Selection([('draft', 'Rough draft'), ('confirmed', 'confirmado'),('done', 'Done')], "Status",track_visibility='always', default='draft')

class TechnicalSupportChecklist(models.Model):
    _name="technical_support.checklist"
    _description= "Checklist"
    _order = 'sequence, id'

    name=fields.Char("Title", required=True)
    active=fields.Boolean("Active", default=1)
    planned_date=fields.Float("Expected Duration")
    sequence=fields.Integer('Sequence')
    description=fields.Text('Description')
    questions_ids=fields.One2many("technical_support.question","checklist_id","Questions")
    models_id=fields.Many2one('equipment.model', u'Model')


    @api.multi
    def copy(self, default=None):
        if default is None:
            default = {}
        context = {}
        if not default.get('name'):
            default.update(name=("%s (copy)") % (self.name))
        res = super(TechnicalSupportChecklist, self).copy(default)
        return res

class TechnicalSupportAnswerHistory(models.Model):
    _name="technical_support.answer.history"
    _description= "Answers"
    _order = 'sequence, id'

    CHOICE_MAINT = [
        ('fait','Made'),
        ('bon','Good'),
        ('mauvais','Bad'),
        ('inapplicable','Inapplicable')]

    name=fields.Char(u"Acción a realizar",required=True)
    sequence=fields.Integer('Sequence')
    question_id=fields.Many2one('technical_support.question', u'Question')
    checklist_history_id=fields.Many2one('technical_support.checklist.history', u'Control List')
    answer=fields.Selection(CHOICE_MAINT, u"State")
    detail=fields.Char(u"Detail")

class TechnicalSupportQuestion(models.Model):
    _name = "technical_support.question"
    _description = "Question"
    _order = 'sequence'

    name=fields.Char("Question", required=True)
    sequence=fields.Integer('Sequence')
    checklist_id=fields.Many2one('technical_support.checklist', 'Control List', required=True)

class TechnicalSupportOrderSignatureLine(models.Model):
    _name = 'technical_support.order.signature.line'
    _description = 'Technical Support Order Signature Line'

    name = fields.Char('Description', size=64)
    user_id=fields.Many2one('res.users', string='Usuarios', required=True)
    maintenance_id = fields.Many2one('technical_support.order', string='Order')

class TechnicalSupportOrderSignatureClientLine(models.Model):
    _name = 'technical_support.order.signature.client.line'
    _description = 'Technical Support Order Signature Client Line'

    name = fields.Char('Description', size=64)
    user_id=fields.Many2one('res.partner', string='Client', required=True)
    maintenance_id = fields.Many2one('technical_support.order', string='Order')
