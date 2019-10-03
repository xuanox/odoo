# -*- coding: utf-8 -*-

from odoo import api, fields, models


class RegulatoryTechnicalFileRegistryLost(models.TransientModel):
    _name = 'regulatory.technical.file.registry.lost'
    _description = 'Get Lost Reason'

    lost_reason_id = fields.Many2one('regulatory.technical.file.registry.lost.reason', 'Lost Reason')
    description=fields.Text('Description')

    @api.multi
    def action_lost_reason_apply(self):
        registry = self.env['regulatory.technical.file.registry'].browse(self.env.context.get('active_ids'))
        registry.write({'lost_reason': self.lost_reason_id.id})
        registry.write({'description_lost':self.description})
        return registry.action_set_fails()
