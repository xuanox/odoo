# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo
#    Copyright (C) 2013-2019 CodUP (<http://codup.com>).
#
##############################################################################

from odoo import api, fields, models
from odoo import netsvc

class HelpdeskTicketPending(models.TransientModel):
    _name = 'helpdesk.ticket.pending'
    _description = 'Pending Ticket'

    pending_reason_id = fields.Many2one('helpdesk.ticket.pending.reason', 'Pending Reason')
    detail_reason = fields.Text('Detail')

    def pending_ticket(self):
        active_id = self._context.get('active_id')
        if active_id:
            ticket = self.env['helpdesk.ticket'].browse(self._context.get('active_id'))
            ticket.write({'detail_reason':self.detail_reason})
            ticket.write({'pending_reason': self.pending_reason_id.id})
            ticket.action_pending()
        return {'type': 'ir.actions.act_window_close',}
