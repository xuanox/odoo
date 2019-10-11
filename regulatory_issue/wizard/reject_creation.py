# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo
#    Copyright (C) 2013-2019 CodUP (<http://codup.com>).
#
##############################################################################

from odoo import api, fields, models
from odoo import netsvc

class RegulatoryTechnicalFileCreationReject(models.TransientModel):
    _name = 'regulatory.technical.file.creation.reject'
    _description = 'Creation Reject'

    reason_id = fields.Many2one('regulatory.lost.reason', required=True, string='Reason')
    description=fields.Text('Detail')

    def reject_creation(self):
        active_id = self._context.get('active_id')
        if active_id:
            registry = self.env['regulatory.technical.file.creation'].browse(self._context.get('active_id'))
            registry.write({'reject_reason_id':self.reason_id.id})
            registry.write({'description_reject':self.description})
            registry.action_rejected()
        return {'type': 'ir.actions.act_window_close'}
