# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo
#    Copyright (C) 2013-2019 CodUP (<http://codup.com>).
#
##############################################################################

from odoo import api, fields, models
from odoo import netsvc

class TechnicalSupportConfirmDone(models.TransientModel):
    _name = 'technical_support.confirm.done'
    _description = 'Confirm Done Order'

    detail = fields.Text('Detail', required=True)

    def confirm_done(self):
        active_id = self._context.get('active_id')
        if active_id:
            request = self.env['technical_support.order'].browse(self._context.get('active_id'))
            request.action_done()
        return {'type': 'ir.actions.act_window_close',}
