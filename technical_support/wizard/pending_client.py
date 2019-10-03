# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo
#    Copyright (C) 2013-2019 CodUP (<http://codup.com>).
#
##############################################################################

from odoo import api, fields, models
from odoo import netsvc

class TechnicalSupportPendingClient(models.TransientModel):
    _name = 'technical_support.pending.client'
    _description = 'Pending Client'

    detail = fields.Text('Detail')

    def pending_client(self):
        active_id = self._context.get('active_id')
        if active_id:
            request = self.env['technical_support.request'].browse(self._context.get('active_id'))
            request.write({'detail_pending_client':self.detail})
            request.action_waiting_for_customer()
        return {'type': 'ir.actions.act_window_close'}
