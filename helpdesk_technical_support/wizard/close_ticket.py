# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo
#    Copyright (C) 2013-2019 CodUP (<http://codup.com>).
#
##############################################################################

from odoo import api, fields, models
from odoo import netsvc

class TechnicalSupportCloseTicket(models.TransientModel):
    _name = 'technical_support.close.ticket'
    _description = 'Close Ticket'

    detail = fields.Text('Detail')

    def close_ticket(self):
        active_id = self._context.get('active_id')
        if active_id:
            request = self.env['technical_support.order'].browse(self._context.get('active_id'))
            request.action_done()
        return {'type': 'ir.actions.act_window_close',}
