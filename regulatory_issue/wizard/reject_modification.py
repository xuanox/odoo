# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo
#    Copyright (C) 2013-2019 CodUP (<http://codup.com>).
#
##############################################################################

from odoo import api, fields, models
from odoo import netsvc

class RegulatoryTechnicalFileModificationReject(models.TransientModel):
    _name = 'regulatory.technical.file.modification.reject'
    _description = 'Modification Reject'

    reason_id = fields.Many2one('regulatory.lost.reason', required=True, string='Reason')
    description=fields.Text('Detail')

    def reject_modification(self):
        active_id = self._context.get('active_id')
        if active_id:
            registry = self.env['regulatory.technical.file.modification'].browse(self._context.get('active_id'))
            registry.write({'reject_reason_id':self.reason_id.id})
            registry.write({'description_reject':self.description})
            registry.action_rejected()
        return {'type': 'ir.actions.act_window_close'}
