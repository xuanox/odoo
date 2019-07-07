# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class Lead(models.Model):
    _inherit = 'crm.lead'

    category_id=fields.Many2one('crm.lead.category', string='Category')
    model_id=fields.Many2one('equipment.model', string='Model')
    date_deadline = fields.Date(required=True)

class CrmLeadCategory(models.Model):
    _name = "crm.lead.category"
    _description = "Sales Category"

    name=fields.Char("Category", required=True)
    description=fields.Text('Description')

class CrmLeadChecklistDemo(models.Model):
    _name = "crm.lead.checklist.demo"
    _description = "Checklist Demo"
    _order = 'sequence'

    name=fields.Char("Item", required=True)
    sequence=fields.Integer('Sequence')
    description=fields.Text('Description')
