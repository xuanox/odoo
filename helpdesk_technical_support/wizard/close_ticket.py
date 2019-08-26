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

    detail_cause = fields.Text('Detail')
    cause_reason = fields.Many2one('helpdesk.ticket.cause.reason', string='Cause', index=True, track_visibility='onchange')
    remote = fields.Boolean('Remote Attention', copy=False)
    close_order = fields.Boolean('Close Order Only', copy=False)
    close_order_ticket = fields.Boolean('Close Order and Ticket', copy=False)

    def close_ticket(self):
        active_id = self._context.get('active_id')
        if active_id:
            request = self.env['technical_support.order'].browse(self._context.get('active_id'))
            request.write({'detail_cause':self.detail_cause})
            request.write({'cause_reason': self.cause_reason.id})
            request.write({'remote':self.remote})
            request.write({'close_order':self.close_order})
            request.write({'close_ticket':self.close_ticket})
            request.ticket_done()
            request.action_done()
        return {'type': 'ir.actions.act_window_close',}

    def close_order_done(self):
        active_id = self._context.get('active_id')
        if active_id:
            request = self.env['technical_support.order'].browse(self._context.get('active_id'))
            request.action_done()
        return {'type': 'ir.actions.act_window_close',}
