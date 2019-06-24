# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo
#    Copyright (C) 2013-2019 CodUP (<http://codup.com>).
#
##############################################################################

from odoo import api, fields, models
from odoo import netsvc

class TechnicalSupportConfirmClient(models.TransientModel):
    _name = 'technical_support.confirm.client'
    _description = 'Confirm Client'

    detail = fields.Text('Detail', required=True)

    def confirm_client(self):
        active_id = self._context.get('active_id')
        if active_id:
            request = self.env['technical_support.request'].browse(self._context.get('active_id'))
            request.write({'detail_confirm_client':self.detail})
            request.action_confirm_client()
        return {'type': 'ir.actions.act_window_close',}
