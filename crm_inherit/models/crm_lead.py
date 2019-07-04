# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class Lead(models.Model):
    _inherit = 'crm.lead'

    modality = fields.Selection([('high', 'High Tech'), ('low', 'Low Tech')], string='Modality')
    model_id=fields.Many2one('equipment.model', string='Model')
    date_deadline = fields.Date(required=True)
