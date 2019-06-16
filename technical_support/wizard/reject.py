# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo
#    Copyright (C) 2013-2019 CodUP (<http://codup.com>).
#
##############################################################################

from odoo import api, fields, models
from odoo import netsvc

class technical_support_request_reject(models.TransientModel):
    _name = 'technical_support.request.reject'
    _description = 'Reject Request'

    reject_reason = fields.Text('Reject Reason', required=True)

    def reject_request(self):
        active_id = self._context.get('active_id')
        if active_id:
            request = self.env['technical_support.request'].browse(self._context.get('active_id'))
            request.write({'reject_reason':self.reject_reason})
            request.action_reject()
        return {'type': 'ir.actions.act_window_close',}
