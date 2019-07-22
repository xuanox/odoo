# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class Lead(models.Model):
    _inherit = 'crm.lead'

    category_id=fields.Many2one('crm.lead.category', string='Category')
    modality_id=fields.Many2one('equipment.modality', string='Modality')
    model_id=fields.Many2one('equipment.model', string='Model')
    date_deadline = fields.Date(required=True)

class CrmLeadCategory(models.Model):
    _name = "crm.lead.category"
    _description = "Sales Category"

    name = fields.Char("Category", required=True)
    team_ids = fields.Many2many('crm.team', relation='team_category_rel', string='Sales Team')
    description = fields.Text('Description')

class CrmLeadChecklistDemo(models.Model):
    _name = "crm.lead.checklist.demo"
    _description = "Checklist Demo"
    _order = 'sequence'

    name=fields.Char("Item", required=True)
    opportunity_id=fields.Many2one('crm.lead', string='Opportunity', domain="[('type', '=', 'opportunity')]")
    partner_id = fields.Many2one(
        'res.partner', 'Contact',
        index=True,
        help='Choose partner for whom the order will be invoiced and delivered. You can find a partner by its Name, TIN, Email or Internal Reference.')
    address_id = fields.Many2one(
        'res.partner', 'Delivery Address',
        domain="[('parent_id','=',partner_id)]")
    default_address_id = fields.Many2one('res.partner', compute='_compute_default_address_id')
    access_path= fields.Text('Ruta de Acceso')
    date_planned = fields.Datetime('Delivery Time', required=True, readonly=True, states={'draft':[('readonly',False)]}, default=time.strftime('%Y-%m-%d %H:%M:%S'), track_visibility='onchange')
    retirement_date = fields.Datetime('Retirement Date', required=True, readonly=True, states={'draft':[('readonly',False)]}, default=time.strftime('%Y-%m-%d %H:%M:%S'), track_visibility='onchange')
    special_delivery_procedure=fields.Text('Description')
    note=fields.Text('Description')

    @api.one
    @api.depends('partner_id')
    def _compute_default_address_id(self):
        if self.partner_id:
            self.default_address_id = self.partner_id.address_get(['contact'])['contact']

class Team(models.Model):
    _inherit = 'crm.team'

    category_ids = fields.Many2many('crm.lead.category', relation='team_category_rel', string='Categories')
