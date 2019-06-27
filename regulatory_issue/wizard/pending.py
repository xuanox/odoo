# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo
#    Copyright (C) 2013-2019 CodUP (<http://codup.com>).
#
##############################################################################

from odoo import api, fields, models
from odoo import netsvc

class RegulatoryIssuePendingRequest(models.TransientModel):
    _name = 'regulatory.issue.pending.request'
    _description = 'Pending Request'

    detail = fields.Text('Detail')

    def pending_request(self):
        active_id = self._context.get('active_id')
        if active_id:
            request = self.env['regulatory.technical.file.registry'].browse(self._context.get('active_id'))
            request.write({'detail':self.detail})
            ticket.action_pending()
        return {'type': 'ir.actions.act_window_close',}
