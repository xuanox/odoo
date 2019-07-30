# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import time
from odoo import api, fields, models
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare

class Lead(models.Model):
    _inherit = 'crm.lead'

    category_id=fields.Many2one('crm.lead.category', string='Category', domain="[('team_ids', '=', team_id)]")
    modality_id=fields.Many2one('equipment.modality', string='Modality', domain="[('category_id', '=', category_id)]")
    model_id=fields.Many2one('equipment.model', string='Model')
    date_deadline = fields.Date(required=True)
    demo = fields.Boolean('Demo', default=False)

    download_place=fields.Char('Lugar de Descarga')
    place_of_delivery=fields.Char('Lugar de Entrega')
    contact_id=fields.Many2one('res.partner', string='Contact')
    access_path=fields.Char('Ruta de Acceso')
    date_planned=fields.Datetime('Delivery Time', track_visibility='onchange')
    retirement_date=fields.Datetime('Retirement Date', track_visibility='onchange')
    special_delivery_procedure=fields.Text('Procedimiento Especial de Entrega')
    note=fields.Text('Note')
    tool= fields.Boolean('Tool', default=False)
    personal = fields.Boolean('Personal', default=False)
    cost_line = fields.One2many('crm.cost.line', 'opportunity_id', string='Cost Lines', copy=True)
    crm_cost_id = fields.Many2one('crm.cost', 'Checklist', domain="[('category_id', '=', category_id)]")

    @api.onchange('crm_cost_id')
    def onchange_cost(self):
        cost = self.crm_cost_id
        new_checklist_lines = []
        for line in cost.cost_line:
            new_checklist_lines.append([0,0,{
                'name': line.name,
                'description': line.description,
                'apply': line.apply,
                'included_in_the_customer_price': line.included_in_the_customer_price,
                'estimated_cost': line.estimated_cost,
                'comment': line.comment,
                }])
        self.cost_line = new_checklist_lines


class CrmLeadCategory(models.Model):
    _name = "crm.lead.category"
    _description = "Sales Category"

    name = fields.Char("Category", required=True)
    team_ids = fields.Many2many('crm.team', relation='team_category_rel', string='Sales Team')
    description = fields.Text('Description')


class Team(models.Model):
    _inherit = 'crm.team'

    category_ids = fields.Many2many('crm.lead.category', relation='team_category_rel', string='Categories')


class CrmCost(models.Model):
    _name = 'crm.cost'
    _description = 'Crm Cost'

    name = fields.Char('Template', size=64, required=True)
    active = fields.Boolean('Active', default=True)
    category_id=fields.Many2one('crm.lead.category', string='Sales Category')
    cost_lines = fields.One2many('cost.line', 'crm_cost_id', 'Cost Line')


class CostLine(models.Model):
    _name = 'cost.line'
    _description = 'Cost Line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'line desc'

    opportunity_id = fields.Many2one('crm.lead', string='Opportunity')
    line = fields.Integer('Line', default=0)
    name = fields.Char(string='Item', required=True)
    description = fields.Text('Description')
    apply= fields.Boolean('Apply', default=False)
    included_in_the_customer_price= fields.Boolean('included in the customer price', default=False)
    estimated_cost = fields.Float(string='Estimated Cost', digits=dp.get_precision('Product Price'))
    comment = fields.Text('Comment')
    category_id=fields.Many2one('crm.lead.category', string='Sales Category')
    crm_cost_id = fields.Many2one('crm.cost', 'Cost')


class CrmCostLine(models.Model):
    _name = 'crm.cost.line'
    _description = 'Crm Cost Line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'line desc'

    opportunity_id = fields.Many2one('crm.lead', string='Opportunity')
    line = fields.Integer('Line', default=0)
    name = fields.Char(string='Item', required=True)
    description = fields.Text('Description')
    apply= fields.Boolean('Apply', default=False)
    included_in_the_customer_price= fields.Boolean('included in the customer price', default=False)
    estimated_cost = fields.Float(string='Estimated Cost', digits=dp.get_precision('Product Price'))
    comment = fields.Text('Comment')
    category_id=fields.Many2one('crm.lead.category', string='Sales Category')
