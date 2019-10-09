# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo
#    Copyright (C) 2013-2019 CodUP (<http://codup.com>).
#
##############################################################################

from odoo import api, fields, models
from odoo import netsvc

class RegulatoryTechnicalFileRegistryReject(models.TransientModel):
    _name = 'regulatory.technical.file.registry.reject'
    _description = 'Registry Reject'

    reject_reason_id = fields.Many2one('regulatory.lost.reason', required=True, string='Reject Reason')
    description=fields.Text('Description')

    def reject_registry(self):
        active_id = self._context.get('active_id')
        if active_id:
            registry = self.env['regulatory.technical.file.registry'].browse(self._context.get('active_id'))
            registry.write({'reject_reason':self.reject_reason_id.id})
            registry.write({'description_reject':self.description})
            registry.action_rejected()
        return {'type': 'ir.actions.act_window_close'}
