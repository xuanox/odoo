# -*- coding: utf-8 -*-

from odoo import api, fields, models


class RegulatoryTechnicalCriteriaUpdateQty(models.TransientModel):
    _name = 'regulatory.technical.criteria.update.qty'
    _description = 'Update Qty TC'

    qty = fields.Integer('Quantity', default=0, help="Assign Quantity.", track_visibility='onchange')

    @api.multi
    def action_update_qty(self):
        registry = self.env['regulatory.technical.criteria'].browse(self.env.context.get('active_ids'))
        registry.write({'qty_available': self.qty})
        return registry.action_check_qty()
