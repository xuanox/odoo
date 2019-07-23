# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import time
from odoo import api, fields, models


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

class CrmLeadCategory(models.Model):
    _name = "crm.lead.category"
    _description = "Sales Category"

    name = fields.Char("Category", required=True)
    team_ids = fields.Many2many('crm.team', relation='team_category_rel', string='Sales Team')
    description = fields.Text('Description')


class Team(models.Model):
    _inherit = 'crm.team'

    category_ids = fields.Many2many('crm.lead.category', relation='team_category_rel', string='Categories')
